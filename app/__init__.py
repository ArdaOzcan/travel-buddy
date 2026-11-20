import os

import psycopg2
from flask import Flask, flash, redirect, render_template, request, url_for

from .db import get_db_connection


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("JWT_SECRET_KEY", "dev-secret-key")

    @app.route("/", methods=["GET"])
    def index():
        city_filter = request.args.get("city", "").strip()
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # Destinations for dropdown
                cur.execute("""
                    SELECT d.destination_id, d.city, c.name AS country_name
                    FROM Destination d
                    JOIN Country c ON d.country_id = c.country_id
                    ORDER BY c.name, d.city;
                """)
                destinations = cur.fetchall()

                # Public trips with optional city filter
                if city_filter:
                    cur.execute(
                        """
                        SELECT t.trip_id, t.traveler_name, t.start_date, t.end_date,
                               t.travel_style, d.city, c.name AS country_name
                        FROM Trip t
                        JOIN Destination d ON t.destination_id = d.destination_id
                        JOIN Country c ON d.country_id = c.country_id
                        WHERE d.city ILIKE %s
                        ORDER BY t.start_date ASC;
                    """,
                        (f"%{city_filter}%",),
                    )
                else:
                    cur.execute("""
                        SELECT t.trip_id, t.traveler_name, t.start_date, t.end_date,
                               t.travel_style, d.city, c.name AS country_name
                        FROM Trip t
                        JOIN Destination d ON t.destination_id = d.destination_id
                        JOIN Country c ON d.country_id = c.country_id
                        ORDER BY t.start_date ASC;
                    """)
                trips = cur.fetchall()
        finally:
            conn.close()

        return render_template(
            "index.html",
            destinations=destinations,
            trips=trips,
            city_filter=city_filter,
        )

    @app.route("/trips", methods=["POST"])
    def create_trip():
        traveler_name = request.form.get("traveler_name", "").strip()
        destination_id = request.form.get("destination_id", "").strip()
        start_date = request.form.get("start_date", "").strip()
        end_date = request.form.get("end_date", "").strip()
        travel_style = request.form.get("travel_style", "budget").strip()

        if not all([traveler_name, destination_id, start_date, end_date]):
            flash("All fields are required.", "error")
            return redirect(url_for("index"))

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO Trip (destination_id, traveler_name, start_date, end_date, travel_style)
                    VALUES (%s, %s, %s, %s, %s);
                """,
                    (destination_id, traveler_name, start_date, end_date, travel_style),
                )
            conn.commit()
            flash("Trip added!", "success")
        except psycopg2.Error as exc:
            conn.rollback()
            flash(f"Database error: {exc.pgerror or exc}", "error")
        finally:
            conn.close()

        return redirect(url_for("index"))

    @app.route("/trips/<int:trip_id>/delete", methods=["POST"])
    def delete_trip(trip_id):
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM Trip WHERE trip_id = %s;", (trip_id,))
            conn.commit()
            flash("Trip deleted.", "success")
        finally:
            conn.close()

        return redirect(url_for("index"))

    return app

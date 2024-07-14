import csv
import time
from datetime import datetime
from typing import Any, Dict, NoReturn

import requests
import schedule
from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout


class ExchangeRateApp(App):
    def build(self):
        self.layout = BoxLayout(orientation="vertical")
        self.buy_label = Label(text="Buy: Fetching...")
        self.sell_label = Label(text="Sell: Fetching...")
        self.layout.add_widget(self.buy_label)
        self.layout.add_widget(self.sell_label)

        # Schedule the job to run every 30 seconds
        schedule.every(30).seconds.do(self.job)
        Clock.schedule_interval(lambda dt: self.run_schedule(), 1)
        return self.layout

    def fetch_exchange_rate(self) -> Dict[str, Any]:
        """Fetch the latest exchange rate from the API."""
        url = "https://criptoya.com/api/usdt/ars"
        response = requests.get(url, timeout=5)
        data = response.json()
        return data.get("buenbit", {})

    def store_exchange_rate_to_csv(self, buy: float, sell: float) -> None:
        """Store the fetched exchange rate into a CSV file."""
        with open("exchange_rates.csv", mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([datetime.now(), "buenbit", buy, sell])

    def job(self) -> None:
        """The scheduled job that fetches and stores the exchange rate."""
        rate_data = self.fetch_exchange_rate()
        if rate_data:
            buy = float(rate_data["totalAsk"])
            sell = float(rate_data["totalBid"])

            self.store_exchange_rate_to_csv(buy=buy, sell=sell)
            self.buy_label.text = f"Buy: {buy}"
            self.sell_label.text = f"Sell: {sell}"
            print(f"Stored new buy: {buy} at {datetime.now()}")
            print(f"Stored new sell: {sell} at {datetime.now()}")

    def check_csv_header(self) -> None:
        try:
            with open("exchange_rates.csv", "x", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Source", "Buy", "Sell"])
        except FileExistsError:
            pass  # File already exists, no need to add headers

    def run_schedule(self) -> None:
        schedule.run_pending()

    def on_start(self):
        self.check_csv_header()
        self.job()  # Run once at start to display initial data


if __name__ == "__main__":
    ExchangeRateApp().run()

from django.core.management.base import BaseCommand
import csv
from ...models import Scrip


class Command(BaseCommand):
    help = 'Imports Nifty 50 scrip data from CSV into the charts.Scrip model'

    def handle(self, *args, **options):
        # Path to your uploaded Nifty 50 CSV file
        csv_path = r"nifty50_stocks.csv"  # Replace with the correct path

        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                total_rows = 0
                processed_rows = 0

                for row in reader:
                    total_rows += 1

                    # Directly use the data from the CSV without modifications
                    symbol = row.get("symbol", "").strip()
                    company_name = row.get("company_name", "").strip()

                    # Create or update the Scrip object in the database
                    try:
                        scrip, created = Scrip.objects.update_or_create(
                            symbol=symbol,
                            defaults={
                                'company_name': company_name,
                            }
                        )
                        processed_rows += 1
                        action = "Created" if created else "Updated"
                        self.stdout.write(self.style.SUCCESS(f"{action} Scrip: {symbol}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error processing Scrip for row: {row}. Error: {e}"))
                        continue

                # Log the final results
                self.stdout.write(self.style.SUCCESS(f"Total rows: {total_rows}"))
                self.stdout.write(self.style.SUCCESS(f"Processed rows: {processed_rows}"))
                self.stdout.write(self.style.SUCCESS('Successfully imported Nifty 50 scrip data into charts.Scrip'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('CSV file not found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))

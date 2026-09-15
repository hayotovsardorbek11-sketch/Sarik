import tempfile
import unittest
from pathlib import Path

import app


class DatabaseConfigurationTest(unittest.TestCase):
    def test_configure_database_creates_database_at_requested_path(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "cinema.db"
            app.configure_database(str(database))

            with app.get_db() as connection:
                tables = {
                    row[0]
                    for row in connection.execute(
                        "SELECT name FROM sqlite_master WHERE type = 'table'"
                    )
                }

            self.assertTrue(database.exists())
            self.assertTrue({"cinema", "users", "comments", "likes_log"}.issubset(tables))


if __name__ == "__main__":
    unittest.main()

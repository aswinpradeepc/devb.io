import json
import os
from datetime import datetime

from config.settings import Settings
from modules.html_generator import HTMLProfileGenerator
from utils.base_command import BaseCommand
from utils.logger import ErrorLogger
from utils.user import get_user_data


class BuildCommand(BaseCommand):

    def process_user(self, username, force=False):
        """
        Comprehensive user profile generation process

        Args:
            username (str): GitHub username to process
        """
        try:
            # Fetch GitHub profile
            if username in Settings.BLACKLISTED_USERS:
                print(f"Skipping blacklisted user: {username}")
                return False
            if force:
                profile_data = get_user_data(username)
            else:
                profile_data = get_user_data(username, force=False)
            # Save raw profile data
            os.makedirs(os.path.join(Settings.DATA_DIR, 'raw_profiles'), exist_ok=True)
            with open(os.path.join(Settings.DATA_DIR, 'raw_profiles', f'{username}_profile.json'), 'w') as f:
                json.dump(profile_data, f, indent=4)

            # Generate HTML profile
            html_generator = HTMLProfileGenerator()
            html_generator.generate_profile_html(
                profile_data,
                Settings.HTML_OUTPUT_DIR
            )
            processed_users = {}
            with open(Settings.PROCESSED_USERS_FILE, 'r') as f:
                processed_users = json.load(f)
            if username not in processed_users:
                processed_users[username] = {
                    'created': datetime.now().isoformat(),
                    'username': username,
                    'avatar_url': profile_data.get('avatar_url', ''),
                    'updated': datetime.now().isoformat(),
                    'name': profile_data.get('name', ''),
                }
            else:
                processed_users[username]['updated'] = datetime.now().isoformat()

            with open(Settings.PROCESSED_USERS_FILE, 'w') as f:
                json.dump(processed_users, f, indent=4)

            print(f"Successfully processed {username}")

            return True
        except Exception as e:
            # Log any errors
            ErrorLogger.log_error(
                username,
                str(e),
            )
            print(f"Error processing {username}: {e}")
            return False

    def run(self, *args):
        """
        a script the clear the generated html files and data files
        """
        """Main execution function"""
        # Load users from JSON
        # if --force is passed, process all users in args
        force = False
        if args and args[0] == '--force':
            force = True
        with open(Settings.DATA_TO_PROCESS, 'r') as f:
            try:
                users = json.load(f)
            except json.JSONDecodeError:
                users = []
        if not users:
            print("No users to process")
            return
        generated_users = []
        for username in users:
            status = self.process_user(username, force)
            if username in users and status:
                generated_users.append(username)
        # Update users list
        users = list(set(users) - set(generated_users))
        with open(Settings.DATA_TO_PROCESS, 'w') as f:
            json.dump(users, f, indent=4)

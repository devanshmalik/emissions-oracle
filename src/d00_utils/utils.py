from dotenv import load_dotenv, find_dotenv
import logging


log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def setup_env_vars():
    log.info("Finding .env file to load entries as environment variables...")
    # find .env automagically by walking up directories until it's found
    dotenv_path = find_dotenv()

    # load up the entries as environment variables
    load_dotenv(dotenv_path)
    log.info("Finished loading environment variables.")
    return




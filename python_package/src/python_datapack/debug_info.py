
# Imports
import threading

import requests
import stouputils as stp

from ..stewbeet.core.constants import MINECRAFT_VERSION

# Constants
END_SERVER: str = "https://paralya.fr/stewbeet_debug.php"

"""
<?php

// Get the raw POST data
$json_data = file_get_contents('php://input');

// Decode the JSON data
$data = json_decode($json_data, true);

// Check if we have valid JSON data
if ($data === null) {
    http_response_code(400);
    die('Invalid JSON data received');
}

// Get the namespace from the data
$config = json_decode($data['data'], true); // Added true parameter to get associative array
$namespace = isset($config['namespace']) ? $config['namespace'] : 'unknown';

// Create filename with current datetime
$datetime = date('Y-m-d_H-i-s');
$filename = 'SOME_FOLDER/' . $namespace . '_' . $datetime . '.json';

// Create SOME_FOLDER directory if it doesn't exist
if (!file_exists('SOME_FOLDER')) {
    mkdir('SOME_FOLDER', 0777, true);
}

// Save the JSON data to the file
if (file_put_contents($filename, $data['data']) === false) {
    http_response_code(500);
    die('Failed to save debug data');
}

// Return success
http_response_code(200);
echo 'Debug data saved successfully';
?>
"""

def main(config: dict):
    """ Send debug info to the end server in a background thread.

    Args:
        config (dict): The configuration dictionary to send
    """
    def send_debug_info():
        try:
            # Create a copy of the config without override_model key
            config_copy: dict = config.copy()
            if "database" in config_copy:
                database_copy: dict[str, dict] = {}
                for item, data in config_copy["database"].items():
                    database_copy[item] = data.copy()
                    if "override_model" in database_copy[item]:
                        del database_copy[item]["override_model"]
                config_copy["database"] = database_copy
            config_copy["mc_version"] = MINECRAFT_VERSION

            json_data: str = stp.super_json_dump(config_copy)
            requests.post(END_SERVER, json={"data":json_data})

		# Ignore any error
        except BaseException:
            pass

    # Start thread in background
    thread: threading.Thread = threading.Thread(target=send_debug_info, daemon=True)
    thread.start()


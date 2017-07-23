"use strict";
const testUrl = process.env.NIGHTWATCH_URL || 'http://127.0.0.1:3001';
const detailedOutput = !!process.env.NIGHTWATCH_DETAIL ;
const parallelTests = !!process.env.PARALLEL;
const parallelWorkers = process.env.PARALLEL_WORKERS || 'auto'; // ignored if PARALLEL is false

import path from 'path';

const glopath = path.join(__dirname,'..');

module.exports = {
  src_folders: ['js'],
  output_folder: 'reports',
  custom_commands_path : [path.join(glopath, 'nightwatch_config', "customCommands")],
  custom_assertions_path: [],
  page_objects_path: '',
  globals_path: path.join(glopath, 'nightwatch_config', "globals.js"),
  detailed_output: detailedOutput,

  selenium: {
     start_process: false,
     server_path: path.join('..',
         'node_modules','selenium-standalone','.selenium','selenium-server','2.53.1-server.jar'),
     log_path: '',
     host: '127.0.0.1',
     port: 4444,
     cli_args: {
       'webdriver.chrome.driver': path.join('..',
           'node_modules','selenium-standalone','.selenium','chromedriver','2.30-x64-chromedriver'),
     }
  },

  test_settings: {
    // default environment. other environments inheret these defaults
    "default" : {
      "launch_url" : testUrl,
      "selenium_port"  : 9515,
      "selenium_host"  : "localhost",
      "default_path_prefix" : "",
      // https://github.com/SeleniumHQ/selenium/wiki/DesiredCapabilities
      "desiredCapabilities": {
        browserName: 'chrome',
        platform: 'ANY',
        javascriptEnabled: true,
        acceptSslCerts: true,
        cssSelectorsEnabled: true,
        locationContextEnabled: false,
        logLevel: 'verbose',
        pageLoadStrategy: 'normal',
        setWindowRect: true,
        loggingPrefs: {
            "browser": "ALL",
            "client": "ALL",
            "driver": "ALL",
            "performance": "ALL",
            "server": "ALL"
        },
        chromeOptions: {
          "args" : ["disable-infobars",  
                    "window-size=1700,1100"
                    ],  // http://peter.sh/experiments/chromium-command-line-switches/
          "prefs" : {
            "credentials_enable_service" : false,
            "profile.password_manager_enabled" : false
          }
        }
       },
      globals : {
        screenshot_path : "latest_images",
        waitForConditionTimeout: 10000,
        isLocal : false,
        end_session_on_fail : true,
      },
      screenshots: {
        enabled: true,
        path: 'latest_images',
      },
      test_workers: {
        enabled: parallelTests,
        workers: parallelWorkers,
      },
      use_xpath: false,
    },

    local_chrome: {
      launch_url    : testUrl,
      selenium_port : 9515,
      selenium_host : "localhost",
      globals : {
        // This will create a local chromedriver when this is true. Selenium/start_process should be false when this is true
        isLocal : true,
        // "end_session_on_fail" : false,
      }
    },
  }
};

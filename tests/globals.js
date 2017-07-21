"use strict";
const pauseOnFail = process.env.NIGHTWATCH_PAUSE_ON_FAIL || 'false';
var chromedriver  = require('chromedriver');
var util = require ('util');

module.exports = {

  // External before hook is ran at the beginning of the tests run, before creating the chromedriver session
  // This will be run after each test suite (e.g. a test file) is started
  before: function(done) {
    // set isLocal in a globals block in your test config or test default
    // run this only for the local-env
    if (this.isLocal) {
      chromedriver.start();
      done();
      
    } else {
      done();
    }
  },

  // External after hook is ran at the very end of the tests run, after closing the Selenium session
  after: function(done) {
    // run this only for the local-env
    if (this.isLocal) {
      chromedriver.stop();      
      done();

    } else {
      done();
    }
  },

  // This will be run before each test case (e.g. a function with a test file) is started
  beforeEach: function(browser, done) {
    // getting the session info
    browser.status(function(result) {
      console.log(result.value);

      done();
    });
  },

  // This will be run after each test case  (e.g. a function with a test file)is finished
  afterEach: function(browser, done) {
    console.log(browser.currentTest);

    done();
  }
};

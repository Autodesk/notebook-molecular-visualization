const widgetUtils = {
  /**
   * Returns a function that calls all given functions
   */
  getMultiFunction(...fns) {
    return function(...args) {
      fns.forEach((fn) => {
        fn && fn.apply(this, args);
      });
    };
  },
};

export default widgetUtils;

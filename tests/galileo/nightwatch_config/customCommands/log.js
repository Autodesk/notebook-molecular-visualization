exports.command = function(str){
    this.perform(
        function(){console.log(str)}
    );

    return this;
};
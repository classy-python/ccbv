// Auto-expand accordian if url contains a valid hash
(function(doc){
    "use strict";

    var DOMReady = function(a){
        var b = doc, c = 'addEventListener';
        b[c] ? b[c]('DOMContentLoaded', a): window.attachEvent('onload', a);
    };

    DOMReady(function() {
        var section, hash = window.location.hash;
        if(hash){
            section = doc.querySelector(hash);
            section.parentNode.querySelector('h3').click();
        }
    });
})(document);

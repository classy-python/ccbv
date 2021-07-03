// Auto-expand the accordion and jump to the target if url contains a valid hash
(function(doc){
    "use strict";

    $(function(event) {
        var hash = window.location.hash;
        var headerHeight = $('.navbar').height();

        if (hash) {
            var $hdr = $(hash).parent('.accordion-group');
            $hdr.prop('open', true);

            // Scroll it into view
            var methodTop = $hdr.offset().top - headerHeight - 8;
            $('html, body').animate({scrollTop: methodTop}, 250);
        }
    });
})(document);

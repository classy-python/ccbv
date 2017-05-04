// Auto-expand the accordion and jump to the target if url contains a valid hash
(function(doc){
    "use strict";

    // On DOM Load...
    $(function(){
        var hash = window.location.hash;
        var headerHeight = $('.navbar').height();
        var methods = $('.accordion-group .accordion-heading');
        var methodCount = methods.length;

        // Sets-up an event handler that will expand and scroll to the desired
        // (hash) method.
        if(hash){
            // We need to know that all the panes have (at least initially)
            // collapsed as a result of loading the page. Unfortunately, we
            // only get events for each collapsed item, so we count...
            $(doc).on('hidden.bs.collapse', function(evt) {
                var methodTop, $hdr = $(hash).parent('.accordion-group');
                methodCount--;
                if(methodCount === 0){
                    // OK, they've /all/ collapsed, now we expand the one we're
                    // interested in the scroll to it.

                    // First, remove this very event handler
                    $(doc).off('hidden.bs.collapse');
                    // Now wait just a beat more to allow the last collapse
                    // animation to complete...
                    setTimeout(function(){
                        // Open the desired method
                        $hdr.find('h3').click();
                        // Take into account the fixed header and the margin
                        methodTop = $hdr.offset().top - headerHeight - 8;
                        // Scroll it into view
                        $('html, body').animate({scrollTop: methodTop}, 250);
                    }, 250);
                }
            });
        }

        // Delegated event handler to prevent the collapse/expand function of
        // a method's header when clicking the Pilcrow (permalink)
        $('.accordion-group').on('click', '.permalink', function(evt){
            evt.preventDefault();
            evt.stopImmediatePropagation();
            window.location = $(this).attr('href');
        });
    })
})(document);

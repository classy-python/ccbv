// Auto-expand the accordion and jump to the target if url contains a valid hash
(function(doc){
    "use strict";

    $(function(){
        var $section, hash = window.location.hash;
        if(hash){
            $section = $(hash);
            if($section){
                $(doc).one('hidden.bs.collapse', hash, function(){
                    $section.parent().find('h3').click();
                });
                $('html, body').animate({
                        scrollTop: $(hash).offset().top
                }, 500);
            }
        }
    })
})(document);

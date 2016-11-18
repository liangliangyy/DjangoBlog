(function ($) {
    $(document).ready(function(){
        /*
         * Admin inline support
         * - this is very finicky at the moment and not ideal. It will be much easier
         *   once custom events are triggered on add/remove of dynamic inlines
         *   https://code.djangoproject.com/ticket/15760
         */
        $('.add-row a, .grp-add-handler').click(function(){
            $(".inline-related:not(.empty-form) fieldset .form-row textarea.wmd-input").each(function(idx, el){
                DjangoPagedown.createEditor(el);

                // Hack 1! Remove second image bar - this seems to be due to the django
                // admin javascript copying the form fromt he first field which
                // means that Pagedown has already rendered the image bar once
                var button_bar = $(this).parents(".wmd-panel").find(".wmd-button-row");
                if ( button_bar.length > 1 ) {
                    button_bar[0].remove();
                }

                // Hack 2! There are no add or remove events triggered by the django
                // so this is workaround to remove Pagedown on removal of inline
                var container = $(this).parents(".inline-related");
                $(container).find(".inline-deletelink").click(function(){
                    DjangoPagedown.destroyEditor(el);
                });
            });
        });
    });
})(django.jQuery);

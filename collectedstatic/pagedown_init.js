var DjangoPagedown = DjangoPagedown | {};

DjangoPagedown = (function() {

    var converter,
        editors,
        elements;

    var that = this;

    var isPagedownable = function(el) {
        if ( (' ' + el.className + ' ').indexOf(' wmd-input ') > -1 ) {
            return true;
        }
        return false;
    };

    var createEditor = function(el) {
        if ( isPagedownable(el) ) {
            if ( ! that.editors.hasOwnProperty(el.id) ) {
                var selectors = {
                    input : el.id,
                    button : el.id + "_wmd_button_bar",
                    preview : el.id + "_wmd_preview",
                };
                that.editors[el.id] = new Markdown.Editor(that.converter, "", selectors);
                that.editors[el.id].run();
                return true;
            } else {
                console.log("Pagedown editor already attached to element: <#" + el.id + ">");
            }
        }
        return false;
    };

    var destroyEditor = function(el) {
        if ( that.editors.hasOwnProperty(el.id)) {
            delete that.editors[el.id];
            return true;
        }
        return false;
    };

    var init = function() {
        that.converter = Markdown.getSanitizingConverter();
        Markdown.Extra.init(that.converter, {
            extensions: "all"
        });
        that.elements = document.getElementsByTagName("textarea");
        that.editors = {};
        for (var i = 0; i < that.elements.length; ++i){
            if ( isPagedownable(that.elements[i]) ) {
                createEditor(that.elements[i]);
            }
        }
    };

    return {
        init: function() {
            return init();
        },
        createEditor: function(el) {
            return createEditor(el);
        },
        destroyEditor: function(el) {
            return destroyEditor(el);
        },
    };
})();

window.onload = DjangoPagedown.init;
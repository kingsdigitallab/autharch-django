(function ( $ ) {
 
    $.fn.richTextTranscriptions = function( options ) {

        // set default options
        // and merge them with the parameter options
        var settings = $.extend({
            
            // text formatting
            inserted: true,
            deleted: true,
            underline: true,
            pageBreak: true,

            // lists
            ol: true,
            ul: true,

            // code
            removeStyles: true,

            // translations
            translations: {
                'title': 'Title',
                'inserted': 'Inserted',
                'deleted': 'Inserted',
                'italic': 'Italic',
                'underline': 'Underline',
                'addOrderedList': 'Add ordered list',
                'addUnorderedList': 'Add unordered list',
                'removeStyles': 'Remove styles',
                'undo': 'Undo',
                'redo': 'Redo',
                'close': 'Close'
            },

            teiTags: {
                'inserted': {
                    'tag': 'ins',
                    'class': 'tei-add',
                    'conflict': 'del'
                },
                'deleted': {
                    'tag': 'del',
                    'class': 'tei-del',
                    'conflict': 'ins'
                }
            },

            // dev settings
            useSingleQuotes: false,
            height: 0,
            heightPercentage: 0,
            id: "",
            class: "",
            useParagraph: false,
            maxlength: 0

            // colors, dropdowns, tables, links, media, uploads, fonts, title, privacy

        }, options );


        /* prepare toolbar */
        var $inputElement = $(this);
        $inputElement.addClass("richText-initial");
        var $editor,
            $toolbarList = $('<ul />'),
            $toolbarElement = $('<li />'),

            $btnInserted = $('<a />', {
                class: "richText-btn richText-btn-icon", 
                "data-command": "inserted", 
                "title": settings.translations.inserted, 
                html: '<span title="inserted text">ins</span>'
            }), // inserted
            $btnDeleted = $('<a />', {
                class: "richText-btn richText-btn-icon", 
                "data-command": "deleted", 
                "title": settings.translations.deleted, 
                html: '<span title="deleted text">del</span>'
            }), // deleted
            $btnPagebreak = $('<a />', {
                class: "richText-btn richText-btn-icon", 
                "data-command": "pagebreak", 
                "title": settings.translations.pageBreak, 
                html: '<span title="page break">pb</span>',
                onclick: function() {
                }
            }), // pagebreak
            $btnUnderline = $('<a />', {
                class: "richText-btn", 
                "data-command": "underline", 
                "title": settings.translations.underline, 
                html: '<span class="fa fa-underline"></span>'}), // underline
            $btnOL = $('<a />', {
                class: "richText-btn", 
                "data-command": "insertOrderedList", 
                "title": settings.translations.addOrderedList, 
                html: '<span class="fa fa-list-ol"></span>'
            }), // ordered list
            $btnUL = $('<a />', {
                class: "richText-btn", 
                "data-command": "insertUnorderedList", 
                "title": settings.translations.addUnorderedList, 
                html: '<span class="fa fa-list"></span>'
            }), // unordered list
            $btnRemoveStyles = $('<a />', {
                class: "richText-btn", 
                "data-command": "removeFormat", 
                "title": settings.translations.removeStyles, 
                html: '<span class="fa fa-recycle"></span>'
            }) // clean up styles

        /* internal settings */
        var savedSelection; // caret position/selection
        var editorID = "richText-" + Math.random().toString(36).substring(7);
        // var ignoreSave = false, $resizeImage = null;

        /* prepare editor history */
        var history = [];
        history[editorID] = [];
        var historyPosition = [];
        historyPosition[editorID] = 0;

        /* initizalize editor */
        function init() {
            var value, attributes, attributes_html = '';

            if(settings.useParagraph !== false) {
                // set default tag when pressing ENTER to <br> instead of <div>
                // TODO add class
                document.execCommand("DefaultParagraphSeparator", false, 'br');
            }

            // reformat $inputElement to textarea
            if($inputElement.prop("tagName") === "TEXTAREA") {
                // everything perfect
            } else if($inputElement.val()) {
                value = $inputElement.val();
                attributes = $inputElement.prop("attributes");
                // loop through <select> attributes and apply them on <div>
                $.each(attributes, function() {
                    if(this.name) {
                        attributes_html += ' ' + this.name + '="' + this.value + '"';
                    }
                });
                $inputElement.replaceWith($('<textarea' + attributes_html + ' data-richtext="init">' + value + '</textarea>'));
                $inputElement = $('[data-richtext="init"]');
                $inputElement.removeAttr("data-richtext");
            } else if($inputElement.html()) {
                value = $inputElement.html();
                attributes = $inputElement.prop("attributes");
                // loop through <select> attributes and apply them on <div>
                $.each(attributes, function() {
                    if(this.name) {
                        attributes_html += ' ' + this.name + '="' + this.value + '"';
                    }
                });
                $inputElement.replaceWith($('<textarea' + attributes_html + ' data-richtext="init">' + value + '</textarea>'));
                $inputElement = $('[data-richtext="init"]');
                $inputElement.removeAttr("data-richtext");
            } else {
                attributes = $inputElement.prop("attributes");
                // loop through <select> attributes and apply them on <div>
                $.each(attributes, function() {
                    if(this.name) {
                        attributes_html += ' ' + this.name + '="' + this.value + '"';
                    }
                });
                $inputElement.replaceWith($('<textarea' + attributes_html + ' data-richtext="init"></textarea>'));
                $inputElement = $('[data-richtext="init"]');
                $inputElement.removeAttr("data-richtext");
            }

            $editor = $('<div />', {class: "richText"});
            var $toolbar = $('<div />', {class: "richText-toolbar"});
            var $editorView = $('<div />', {class: "richText-editor", id: editorID, contenteditable: true});
            $toolbar.append($toolbarList);

            /* text formatting */
            if(settings.inserted === true) {
                $toolbarList.append($toolbarElement.clone().append($btnInserted));
            }
            if(settings.deleted === true) {
                $toolbarList.append($toolbarElement.clone().append($btnDeleted));
            }
            // if(settings.pageBreak === true) {
            //     $toolbarList.append($toolbarElement.clone().append($btnPagebreak));
            // }
            if(settings.underline === true) {
                $toolbarList.append($toolbarElement.clone().append($btnUnderline));
            }

            /* lists */
            if(settings.ol === true) {
                $toolbarList.append($toolbarElement.clone().append($btnOL));
            }
            if(settings.ul === true) {
                $toolbarList.append($toolbarElement.clone().append($btnUL));
            }

            /* removeStyles */
            // if(settings.removeStyles === true) {
            //     $toolbarList.append($toolbarElement.clone().append($btnRemoveStyles));
            // }

            // convert a string from the input element to an HTML object 
            var htmlObject = $.parseHTML($inputElement.val())[1];
            // make sure the inserted content is for TEI
            if (!$(htmlObject).hasClass('tei-body')) {
                // add the 'tei-body' class to the wrapper tag
                $(htmlObject).addClass('tei-body');
            }
            $(htmlObject).find('br[class="tei-lb"]').each(function() {
                $(this).after(' ');
            });
            $(htmlObject).children().each(function() {
                $(this).prepend(' ');
            });
            // set an updated textarea value to editor
            $editorView.html(htmlObject);

            $editor.append($toolbar);
            $editor.append($editorView);
            $editor.append($inputElement.clone().hide());
            $inputElement.replaceWith($editor);

            // append bottom toolbar
            $editor.append(
                $('<div />', {class: 'richText-toolbar'})
                    .append($('<a />', {class: 'richText-undo is-disabled', html: '<span class="fa fa-undo"></span>', 'title': settings.translations.undo}))
                    .append($('<a />', {class: 'richText-redo is-disabled', html: '<span class="fa fa-repeat fa-redo"></span>', 'title': settings.translations.redo}))
            );

            if(settings.maxlength > 0) {
                // display max length in editor toolbar
                $editor.data('maxlength', settings.maxlength);
                //changed richtext-help to richtext-undo
                $editor.children('.richText-toolbar').children('.richText-undo').before($('<a />', {class: 'richText-length', text: '0/' + settings.maxlength}));
            }

            if(settings.height && settings.height > 0) {
                // set custom editor height
                $editor.children(".richText-editor, .richText-initial").css({'min-height' : settings.height + 'px', 'height' : settings.height + 'px'});
            } else if(settings.heightPercentage && settings.heightPercentage > 0) {
                // set custom editor height in percentage
                var parentHeight = $editor.parent().innerHeight(); // get editor parent height
                var height = (settings.heightPercentage/100) * parentHeight; // calculate pixel value from percentage
                height -= $toolbar.outerHeight()*2; // remove toolbar size
                height -= parseInt($editor.css("margin-top")); // remove margins
                height -= parseInt($editor.css("margin-bottom")); // remove margins
                height -= parseInt($editor.find(".richText-editor").css("padding-top")); // remove paddings
                height -= parseInt($editor.find(".richText-editor").css("padding-bottom")); // remove paddings
                $editor.children(".richText-editor, .richText-initial").css({'min-height' : height + 'px', 'height' : height + 'px'});
            }

            // add custom class
            if(settings.class) {
                $editor.addClass(settings.class);
            }
            if(settings.id) {
                $editor.attr("id", settings.id);
            }

            // fix the first line
            // OL - commented out; need to test the editor based on the inputted content
            // fixFirstLine();

            // save history
            history[editorID].push($editor.find("textarea").val());
        }

        // initialize editor
        init();


        /** EVENT HANDLERS */

        // undo / redo
        $(document).on("click", ".richText-undo, .richText-redo", function(e) {
             var $this = $(this);
             var $editor = $this.parents('.richText');
             if($this.hasClass("richText-undo") && !$this.hasClass("is-disabled")) {
                 undo($editor);
             } else if($this.hasClass("richText-redo") && !$this.hasClass("is-disabled")) {
                 redo($editor);
             }
        });


        // Saving changes from editor to textarea
        $(document).on("input change blur keydown keyup", ".richText-editor", function(e) {
            if((e.keyCode === 9 || e.keyCode === "9") && e.type === "keydown") {
                // tab through table cells
                e.preventDefault();
                tabifyEditableTable(window, e);
                return false;
            }
            // OL - commented out as the method wraps p and br tags with divs
            // fixFirstLine();
            updateTextarea();
            doSave($(this).attr("id"));
            updateMaxLength($(this).attr('id'));
        });


        // add context menu to several Node elements
        $(document).on('contextmenu', '.richText-editor', function(e) {

            var $list = $('<ul />', {'class': 'list-rightclick richText-list'});
            var $li = $('<li />');
            // remove Node selection
            $('.richText-editor').find('.richText-editNode').removeClass('richText-editNode');

            var $target = $(e.target);
            var $richText = $target.parents('.richText');
            // var $toolbar = $richText.find('.richText-toolbar');

            var positionX = e.pageX - $richText.offset().left;
            var positionY = e.pageY - $richText.offset().top;

            $list.css({
                'top': positionY,
                'left': positionX
            });

        });

        // Saving changes from textarea to editor
        $(document).on("input change blur", ".richText-initial", function() {
            if(settings.useSingleQuotes === true) {
                $(this).val(changeAttributeQuotes($(this).val()));
            }
            var editorID = $(this).siblings('.richText-editor').attr("id");
            updateEditor(editorID);
            doSave(editorID);
            updateMaxLength(editorID);
        });

        // Save selection seperately (mainly needed for Safari)
        $(document).on("dblclick mouseup", ".richText-editor", function() {
            var editorID = $(this).attr("id");
            doSave(editorID);
        });

        // Executing editor commands
        $(document).on("click", ".richText-toolbar a[data-command]", function(event) {
            var $button = $(this);
            var $toolbar = $button.closest('.richText-toolbar');
            var $editor = $toolbar.siblings('.richText-editor');
            var id = $editor.attr("id");
            if($editor.length > 0 && id === editorID && (!$button.parent("li").attr('data-disable') || $button.parent("li").attr('data-disable') === "false")) {
                event.preventDefault();
                var command = $(this).data("command");

                if(command === "toggleCode") {
                    toggleCode($editor.attr("id"));
                } else {
                    var option = null;
                    if ($(this).data('option')) {
                        option = $(this).data('option').toString();
                        if (option.match(/^h[1-6]$/)) {
                            command = "heading";
                        }
                    }

                    formatText(command, option, id);
                    if (command === "removeFormat") {
                        // remove HTML/CSS formatting
                        $editor.find('*').each(function() {
                            // remove all, but very few, attributes from the nodes
                            var keepAttributes = [
                                "id", "class",
                                "name", "action", "method",
                                "src", "align", "alt", "title",
                                "style", "webkitallowfullscreen", "mozallowfullscreen", "allowfullscreen",
                                "width", "height", "frameborder"
                            ];
                            var element = $(this);
                            var attributes = $.map(this.attributes, function(item) {
                                return item.name;
                            });
                            $.each(attributes, function(i, item) {
                                if(keepAttributes.indexOf(item) < 0 && item.substr(0, 5) !== 'data-') {
                                    element.removeAttr(item);
                                }
                            });
                            // OL - we don't need to embed links
                            // if(element.prop('tagName') === "A") {
                            //     // remove empty URL tags
                            //     element.replaceWith(function() {
                            //         return $('<span />', {html: $(this).html()});
                            //     });
                            // }
                        });
                        formatText('formatBlock', 'div', id);
                    }
                    // clean up empty tags, which can be created while replacing formatting or when copy-pasting from other tools
                    $editor.find('div:empty,p:empty,li:empty,h1:empty,h2:empty,h3:empty,h4:empty,h5:empty,h6:empty,del:empty,ins:empty').remove();
                    $editor.find('h1,h2,h3,h4,h5,h6').unwrap('h1,h2,h3,h4,h5,h6');
                }
            }
            // close dropdown after click
            $button.parents('li.is-selected').removeClass('is-selected');
        });



        /** INTERNAL METHODS **/

        /**
         * Format text in editor
         * @param {string} command
         * @param {string|null} option
         * @param {string} editorID
         * @private
         */
        function formatText(command, option, editorID) {
            if (typeof option === "undefined") {
                option = null;
            }
            // restore selection from before clicking on any button
            doRestore(editorID);
            // Temporarily enable designMode so that
            // Execute the command
            if(command === "heading" && getSelectedText()) {
                // IE workaround
                pasteHTMLAtCaret('<' + option + '>' + getSelectedText() + '</' + option + '>');
            } else {
                insertTEI(command);
            }
            
        }


        /**
         * Update textarea when updating editor
         * @private
         */
        function updateTextarea() {
            var $editor = $('#' + editorID);
            var content = $editor.html();
            if(settings.useSingleQuotes === true) {
                content = changeAttributeQuotes(content);
            }
            $editor.siblings('.richText-initial').val(content);
        }


        /**
         * Update editor when updating textarea
         * @private
         */
        function updateEditor(editorID) {
            var $editor = $('#' + editorID);
            var content = $editor.siblings('.richText-initial').val();
            $editor.html(content);
        }


        /**
         * Save caret position and selection
         * @return object
         **/
        function saveSelection(editorID) {
            var containerEl = document.getElementById(editorID);
            var range, start, end, type;
            if(window.getSelection && document.createRange) {
                var sel = window.getSelection && window.getSelection();
                if (sel && sel.rangeCount > 0 && $(sel.anchorNode).parents('#' + editorID).length > 0) {
                    range = window.getSelection().getRangeAt(0);
                    var preSelectionRange = range.cloneRange();
                    preSelectionRange.selectNodeContents(containerEl);
                    preSelectionRange.setEnd(range.startContainer, range.startOffset);
                    
                    start = preSelectionRange.toString().length;
                    end = (start + range.toString().length);

                    type = (start === end ? 'caret' : 'selection');
                    anchor = sel.anchorNode; //(type === "caret" && sel.anchorNode.tagName ? sel.anchorNode : false);
                    start = (type === 'caret' && anchor !== false ? 0 : preSelectionRange.toString().length);
                    end = (type === 'caret' && anchor !== false ? 0 : (start + range.toString().length));

                    return {
                        start: start,
                        end: end,
                        type: type,
                        anchor: anchor,
                        editorID: editorID
                    }
                }
            }
            return (savedSelection ? savedSelection : {
                        start: 0,
                        end: 0
                    });
        }


        /**
         * Restore selection
         **/
        function restoreSelection(editorID, media, url) {
            var containerEl = document.getElementById(editorID);
            var savedSel = savedSelection;
            if(!savedSel) {
                // fix selection if editor has not been focused
                savedSel = {
                    'start': 0,
                    'end': 0,
                    'type': 'caret',
                    'editorID': editorID,
                    'anchor': $('#' + editorID).children('div')[0]
                };
            }

            if(savedSel.editorID !== editorID) {
                return false;
            } else if(media === true) {
                containerEl = (savedSel.anchor ? savedSel.anchor : containerEl); // fix selection issue
            } else if(url === true) {
                if(savedSel.start === 0 && savedSel.end === 0) {
                    containerEl = (savedSel.anchor ? savedSel.anchor : containerEl); // fix selection issue
                }
            }

            if (window.getSelection && document.createRange) {
                var charIndex = 0, range = document.createRange();
                if(!range || !containerEl) { window.getSelection().removeAllRanges(); return true; }
                range.setStart(containerEl, 0);
                range.collapse(true);
                var nodeStack = [containerEl], node, foundStart = false, stop = false;

                while (!stop && (node = nodeStack.pop())) {
                    if (node.nodeType === 3) {
                        var nextCharIndex = charIndex + node.length;
                        if (!foundStart && savedSel.start >= charIndex && savedSel.start <= nextCharIndex) {
                            range.setStart(node, savedSel.start - charIndex);
                            foundStart = true;
                        }
                        if (foundStart && savedSel.end >= charIndex && savedSel.end <= nextCharIndex) {
                            range.setEnd(node, savedSel.end - charIndex);
                            stop = true;
                        }
                        charIndex = nextCharIndex;
                    } else {
                        var i = node.childNodes.length;
                        while (i--) {
                            nodeStack.push(node.childNodes[i]);
                        }
                    }
                }
                var sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(range);
            }
        }



        /**
         * Save caret position and selection
         * @return object
         **/
         /*
        function saveSelection(editorID) {
            var containerEl = document.getElementById(editorID);
            var start;
            if (window.getSelection && document.createRange) {
                var sel = window.getSelection && window.getSelection();
                if (sel && sel.rangeCount > 0) {
                    var range = window.getSelection().getRangeAt(0);
                    var preSelectionRange = range.cloneRange();
                    preSelectionRange.selectNodeContents(containerEl);
                    preSelectionRange.setEnd(range.startContainer, range.startOffset);
                    start = preSelectionRange.toString().length;

                    return {
                        start: start,
                        end: start + range.toString().length,
                        editorID: editorID
                    }
                } else {
                    return (savedSelection ? savedSelection : {
                        start: 0,
                        end: 0
                    });
                }
            } else if (document.selection && document.body.createTextRange) {
                var selectedTextRange = document.selection.createRange();
                var preSelectionTextRange = document.body.createTextRange();
                preSelectionTextRange.moveToElementText(containerEl);
                preSelectionTextRange.setEndPoint("EndToStart", selectedTextRange);
                start = preSelectionTextRange.text.length;

                return {
                    start: start,
                    end: start + selectedTextRange.text.length,
                    editorID: editorID
                };
            }
        }
        */

        /**
         * Restore selection
         **/
         /*
        function restoreSelection(editorID) {
            var containerEl = document.getElementById(editorID);
            var savedSel = savedSelection;
            if(savedSel.editorID !== editorID) {
                return false;
            }
            if (window.getSelection && document.createRange) {
                var charIndex = 0, range = document.createRange();
                range.setStart(containerEl, 0);
                range.collapse(true);
                var nodeStack = [containerEl], node, foundStart = false, stop = false;

                while (!stop && (node = nodeStack.pop())) {
                    if (node.nodeType === 3) {
                        var nextCharIndex = charIndex + node.length;
                        if (!foundStart && savedSel.start >= charIndex && savedSel.start <= nextCharIndex) {
                            range.setStart(node, savedSel.start - charIndex);
                            foundStart = true;
                        }
                        if (foundStart && savedSel.end >= charIndex && savedSel.end <= nextCharIndex) {
                            range.setEnd(node, savedSel.end - charIndex);
                            stop = true;
                        }
                        charIndex = nextCharIndex;
                    } else {
                        var i = node.childNodes.length;
                        while (i--) {
                            nodeStack.push(node.childNodes[i]);
                        }
                    }
                }
                var sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(range);
            } else if (document.selection && document.body.createTextRange) {
                var textRange = document.body.createTextRange();
                textRange.moveToElementText(containerEl);
                textRange.collapse(true);
                textRange.moveEnd("character", savedSel.end);
                textRange.moveStart("character", savedSel.start);
                textRange.select();
            }
        }
        */

        /**
         * Returns the text from the current selection
         * @private
         * @return {string|boolean}
         */
        function getSelectedText() {
            var range;
            if (window.getSelection) {  // all browsers, except IE before version 9
                range = window.getSelection();
                if(range.toString().length > 0) {
                    return range.toString() ? range.toString() : range.focusNode.nodeValue;
                }
            } else  if (document.selection.createRange) { // Internet Explorer
                range = document.selection.createRange();
                return range.text;
            }
            return false;
        }

        /**
         * Save selection
         */
        function doSave(editorID) {
            var $textarea = $('.richText-editor#' + editorID).siblings('.richText-initial');
            addHistory($textarea.val(), editorID);
            savedSelection = saveSelection(editorID);
        }

        /**
         * @param editorID
         * @returns {boolean}
         */
        function updateMaxLength(editorID) {
            var $editorInner = $('.richText-editor#' + editorID);
            var $editor = $editorInner.parents('.richText');
            if(!$editor.data('maxlength')) {
                return true;
            }
            var color;
            var maxLength = parseInt($editor.data('maxlength'));
            var content = $editorInner.text();
            var percentage = (content.length/maxLength)*100;
            if(percentage > 99) {
                color = 'red';
            } else if(percentage >= 90) {
                color = 'orange';
            } else {
                color = 'black';
            }

            $editor.find('.richText-length').html('<span class="' + color + '">' + content.length + '</span>/' + maxLength);

            if(content.length > maxLength) {
                // content too long
                undo($editor);
                return false;
            }
            return true;
        }

        /**
         * Add to history
         * @param val Editor content
         * @param id Editor ID
         */
        function addHistory(val, id) {
            if(!history[id]) {
                return false;
            }
            if(history[id].length-1 > historyPosition[id]) {
                history[id].length = historyPosition[id] + 1;
            }

            if(history[id][history[id].length-1] !== val) {
                history[id].push(val);
            }

            historyPosition[id] = history[id].length-1;
            setHistoryButtons(id);
        }

        function setHistoryButtons(id) {
            if(historyPosition[id] <= 0) {
                $editor.find(".richText-undo").addClass("is-disabled");
            } else {
                $editor.find(".richText-undo").removeClass("is-disabled");
            }

            if(historyPosition[id] >= history[id].length-1 || history[id].length === 0) {
                $editor.find(".richText-redo").addClass("is-disabled");
            } else {
                $editor.find(".richText-redo").removeClass("is-disabled");
            }
        }

        /**
         * Undo
         * @param $editor
         */
        function undo($editor) {
            var id = $editor.children('.richText-editor').attr('id');
            historyPosition[id]--;
            if(!historyPosition[id] && historyPosition[id] !== 0) {
                return false;
            }
            var value = history[id][historyPosition[id]];
            $editor.find('textarea').val(value);
            $editor.find('.richText-editor').html(value);
            setHistoryButtons(id);
        }

        /**
         * Redo
         * @param $editor
         */
        function redo($editor) {
            var id = $editor.children('.richText-editor').attr('id');
            historyPosition[id]++;
            if(!historyPosition[id] && historyPosition[id] !== 0) {
                return false;
            }
            var value = history[id][historyPosition[id]];
            $editor.find('textarea').val(value);
            $editor.find('.richText-editor').html(value);
            setHistoryButtons(id);
        }

        /**
         * Restore selection
         */
        function doRestore(id) {
            if(savedSelection) {
                restoreSelection((id ? id : savedSelection.editorID));
            }
        }


        /**
         * 
         * @param {string} $command 
         */
        function insertTEI(command) { 
            if (settings.teiTags[command]) {
                var sel;
                var tagName = settings.teiTags[command].tag;
                var className = settings.teiTags[command].class;
                // TODO if tei-add then remove tei-del wrapper and vice versa
                if (window.getSelection) {
                    sel = window.getSelection();
                    var el = sel.getRangeAt(0).cloneContents();
                    // check parents - check if the tag already wraps the selected text; if so, untag
                    if (sel.getRangeAt(0).commonAncestorContainer.className == className) {
                        // TODO - unwrap
                    } else {
                        const html = document.createElement(tagName);
                        html.setAttribute('class', className);
                        html.appendChild(el);
                        // check children - make sure the tag is not duplicated in inside the selected tag
                        $(html).children('.'+className).each(function() {
                            $(this).replaceWith($(this).contents());
                        });
                        // make sure there are no empty tags remaining
                        $editor.find('div:empty,p:empty,li:empty,h1:empty,h2:empty,h3:empty,h4:empty,h5:empty,h6:empty,del:empty,ins:empty').remove();
                        const range = sel.getRangeAt(0);
                        range.deleteContents();
                        range.insertNode(html);
                    }
                }
                else if (document.selection && document.selection.type !== "Control") {
                    // IE < 9
                    document.selection.createRange().pasteHTML(html);
                }
            }
            else {
                // document.execCommand() will work
                document.designMode = "ON";
                document.execCommand(command, false, 'div');
                // Disable designMode
                document.designMode = "OFF";
            }
        }

        /**
         * Paste HTML at caret position
         * @param {string} html HTML code
         * @private
         */
        function pasteHTMLAtCaret(html) {
            // add HTML code for Internet Explorer
            var sel, range;
            if (window.getSelection) {
                // IE9 and non-IE
                sel = window.getSelection();
                if (sel.getRangeAt && sel.rangeCount) {
                    
                    range = sel.getRangeAt(0);
                    range.deleteContents();

                    // Range.createContextualFragment() would be useful here but is
                    // only relatively recently standardized and is not supported in
                    // some browsers (IE9, for one)
                    var el = document.createElement("div");
                    el.innerHTML = html;
                    var frag = document.createDocumentFragment(), node, lastNode;
                    while ( (node = el.firstChild) ) {
                        lastNode = frag.appendChild(node);
                    }
                    range.insertNode(lastNode);

                    // Preserve the selection
                    if (lastNode) {
                        range = range.cloneRange();
                        range.setStartAfter(lastNode);
                        range.collapse(true);
                        sel.removeAllRanges();
                        sel.addRange(range);
                    }
                }
            } else if (document.selection && document.selection.type !== "Control") {
                // IE < 9
                document.selection.createRange().pasteHTML(html);
            }
        }


        /**
         * Change quotes around HTML attributes
         * @param  {string} string
         * @return {string}
         */
        function changeAttributeQuotes(string) {
            if(!string) {
                return '';
            }

            var regex;
            var rstring;
            if(settings.useSingleQuotes === true) {
                regex = /\s+(\w+\s*=\s*(["][^"]*["])|(['][^']*[']))+/g;
                rstring = string.replace(regex, function($0,$1,$2){
                    if(!$2) {return $0;}
                    return $0.replace($2, $2.replace(/\"/g, "'"));
                });
            } else {
                regex = /\s+(\w+\s*=\s*(['][^']*['])|(["][^"]*["]))+/g;
                rstring = string.replace(regex, function($0,$1,$2){
                    if(!$2) {return $0;}
                    return $0.replace($2, $2.replace(/'/g, '"'));
                });
            }
            return rstring;
        }


        // /**
        //  * Load colors for font or background
        //  * @param {string} command Command
        //  * @returns {string}
        //  * @private
        //  */
        // function loadColors(command) {
        //     var colors = [];
        //     var result = '';

        //     colors["#FFFFFF"] = settings.translations.white;
        //     colors["#000000"] = settings.translations.black;
        //     colors["#7F6000"] = settings.translations.brown;
        //     colors["#938953"] = settings.translations.beige;
        //     colors["#1F497D"] = settings.translations.darkBlue;
        //     colors["blue"] = settings.translations.blue;
        //     colors["#4F81BD"] = settings.translations.lightBlue;
        //     colors["#953734"] = settings.translations.darkRed;
        //     colors["red"] = settings.translations.red;
        //     colors["#4F6128"] = settings.translations.darkGreen;
        //     colors["green"] = settings.translations.green;
        //     colors["#3F3151"] = settings.translations.purple;
        //     colors["#31859B"] = settings.translations.darkTurquois;
        //     colors["#4BACC6"] = settings.translations.turquois;
        //     colors["#E36C09"] = settings.translations.darkOrange;
        //     colors["#F79646"] = settings.translations.orange;
        //     colors["#FFFF00"] = settings.translations.yellow;

        //     if(settings.colors && settings.colors.length > 0) {
        //         colors = settings.colors;
        //     }

        //     for (var i in colors) {
        //         result += '<li class="inline"><a data-command="' + command + '" data-option="' + i + '" style="text-align:left;" title="' + colors[i] + '"><span class="box-color" style="background-color:' + i + '"></span></a></li>';
        //     }
        //     return result;
        // }


        /**
         * Toggle (show/hide) code or editor
         * @private
         */
        function toggleCode(editorID) {
            doRestore(editorID);
            if($editor.find('.richText-editor').is(":visible")) {
                // show code
                $editor.find('.richText-initial').show();
                $editor.find('.richText-editor').hide(); 
                // disable non working buttons
                $('.richText-toolbar').find('.richText-btn').each(function() {
                    if($(this).children('.fa-code').length === 0) {
                        $(this).parent('li').attr("data-disable", "true");
                    }
                });
                convertCaretPosition(editorID, savedSelection);
            } else {
                // show editor
                $editor.find('.richText-initial').hide();
                $editor.find('.richText-editor').show();
                convertCaretPosition(editorID, savedSelection, true);
                // enable all buttons again
                $('.richText-toolbar').find('li').removeAttr("data-disable");
            }
        }


        /**
         * Convert caret position from editor to code view (or in reverse)
         * @param {string} editorID
         * @param {object} selection
         * @param {boolean} reverse
         **/ 
        function convertCaretPosition(editorID, selection, reverse) {
            var $editor = $('#' + editorID);
            var $textarea = $editor.siblings(".richText-initial");

            var code = $textarea.val();
            if(!selection || !code) {
                return {start: 0, end: 0};
            }

            if(reverse === true) {
                savedSelection = {start: $editor.text().length, end: $editor.text().length, editorID: editorID};
                restoreSelection(editorID);
                return true;
            }
            selection.node = $textarea[0];
            var states = {start: false, end: false, tag: false, isTag: false, tagsCount: 0, isHighlight: (selection.start !== selection.end)};
            for(var i = 0; i < code.length; i++) {
                if(code[i] === "<") {
                    // HTML tag starts
                    states.isTag = true;
                    states.tag = false;
                    states.tagsCount++;
                } else if(states.isTag === true && code[i] !== ">") {
                    states.tagsCount++;
                } else if(states.isTag === true && code[i] === ">") {
                    states.isTag = false;
                    states.tag = true;
                    states.tagsCount++;
                } else if(states.tag === true) {
                    states.tag = false;
                }

                if(!reverse) {
                    if((selection.start + states.tagsCount) <= i && states.isHighlight &&  !states.isTag && !states.tag && !states.start) {
                        selection.start = i;
                        states.start = true;
                    } else if((selection.start + states.tagsCount) <= i+1 && !states.isHighlight &&  !states.isTag && !states.tag && !states.start) {
                        selection.start = i+1;
                        states.start = true;
                    }
                    if((selection.end + states.tagsCount) <= i+1 && !states.isTag && !states.tag && !states.end) {
                        selection.end = i+1;
                        states.end = true;
                    }
                }

            }
            createSelection(selection.node, selection.start, selection.end);
            return selection;
        }

        /**
         * Create selection on node element
         * @param {Node} field
         * @param {int} start
         * @param {int} end
         **/ 
        function createSelection(field, start, end) {
            if( field.createTextRange ) {
                var selRange = field.createTextRange();
                selRange.collapse(true);
                selRange.moveStart('character', start);
                selRange.moveEnd('character', end);
                selRange.select();
                field.focus();
            } else if( field.setSelectionRange ) {
                field.focus();
                field.setSelectionRange(start, end);
            } else if( typeof field.selectionStart != 'undefined' ) {
                field.selectionStart = start;
                field.selectionEnd = end;
                field.focus();
            }
        }

        /**
         * Fix the first line as by default the first line has no tag container
         */
        // function fixFirstLine() {
        //     if($editor && !$editor.find(".richText-editor").html()) {
        //         // set first line with the right tags
        //         if(settings.useParagraph !== false) {
        //             $editor.find(".richText-editor").html('<p><br></p>');
        //         } else {
        //             $editor.find(".richText-editor").html('<div><br></div>');
        //         }
        //     } else {
        //         // replace tags, to force <div> or <p> tags and fix issues
        //         if(settings.useParagraph !== false) {
        //             $editor.find(".richText-editor").find('div:not(.videoEmbed)').replaceWith(function() {
        //                 return $('<p />', {html: $(this).html()});
        //             });
        //         } else {
        //             $editor.find(".richText-editor").find('p').replaceWith(function() {
        //                 return $('<div />', {html: $(this).html()});
        //             });
        //         }
        //     }
        //     updateTextarea();
        // }

        return $(this);
    };

    $.fn.unRichText = function( options ) {

        // set default options
        // and merge them with the parameter options
        var settings = $.extend({
            delay: 0 // delay in ms
        }, options);

        var $editor, $textarea, $main;
        var $el = $(this);

        /**
         * Initialize undoing RichText and call remove() method
         */
        function init() {

            if($el.hasClass('richText')) {
                $main = $el;
            } else if($el.hasClass('richText-initial') || $el.hasClass('richText-editor')) {
                $main = $el.parents('.richText');
            }

            if(!$main) {
                // node element does not correspond to RichText elements
                return false;
            }

            $editor = $main.find('.richText-editor');
            $textarea = $main.find('.richText-initial');

            if(parseInt(settings.delay) > 0) {
                // a delay has been set
                setTimeout(remove, parseInt(settings.delay));
            } else {
                remove();
            }
        }
        init();

        /**
         * Remove RichText elements
         */
        function remove() {
            $main.find('.richText-toolbar').remove();
            $main.find('.richText-editor').remove();
            $textarea
                .unwrap('.richText')
                .data('editor', 'richText')
                .removeClass('richText-initial')
                .show();
        }

    };
 
}( jQuery ));

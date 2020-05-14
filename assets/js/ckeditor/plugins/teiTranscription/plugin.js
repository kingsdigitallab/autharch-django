
CKEDITOR.plugins.add( 'teiTranscription', {
    icons: 'teiPageBreak,teiAdd,teiDel,teiParagraph,teiLineBreak,teiNote,teiUnclear,teiUnderline',
    init: function( editor ) {

        // TODO - REFACTOR

        // TEI-ADD
        editor.addCommand( 'teiAdd', {
            exec: function( editor ) {
                var className = 'tei-add';
                var editorSelection = editor.getSelection();
                var range = editorSelection.getRanges()[ 0 ];
                var el = editor.document.createElement( 'div' );
                el.append(range.cloneContents());
                var commonAncestor = editorSelection.getCommonAncestor();
                //check class of the parent element; if the same as the class of the embedded icon, then unwrap
                if (className === commonAncestor.$.className || className === commonAncestor.$.parentElement.className) {
                    editor.insertHtml(el.getHtml());
                }
                // check if any text was selected so as not to embed an empty tag
                else if (editorSelection.getSelectedText().length > 0) {
                    // resolve a conflict with tei-del
                    /*
                        checks only the closest ancestor; 
                        therefore, if the text is wrapped in <u><del>text</del></u>, the condition is false
                    */
                    if (commonAncestor.$.className == 'tei-del') {
                        range.deleteContents();
                    } 
                    var newElement = new CKEDITOR.dom.element("ins");
                    newElement.setAttributes({class: className});
                    newElement.setHtml(el.getHtml());
                    // check children - make sure the tag is not duplicated in inside the selected tag
                    var children = newElement.find('.'+className+', .tei-del, .tei-p');
                    for ( var i = 0; i < children.count(); i++ ) {
                        children.getItem( i ).$.outerHTML = children.getItem( i ).$.innerHTML;
                    }
                    editor.insertElement(newElement);
                }
                else {
                    return false;
                }
                // clean up the script and remove empty tags
                var elements = editorSelection.document.getBody().getElementsByTag( '*' );
                for ( var i = 0; i < elements.count(); ++i ) {
                    if (elements.getItem(i).$.className !== 'tei-lb' && elements.getItem(i).$.innerHTML.length == 0) {
                        elements.getItem(i).remove();
                    } else if (elements.getItem(i).$.innerHTML == '<br class="tei-lb">') {
                        elements.getItem(i).$.outerHTML = elements.getItem(i).$.innerHTML;
                    }
                }
            }
        });
        editor.ui.addButton('TeiAdd', {
            label: 'tei-add: highlights text that was\ninserted in the source text by an author',
            command: 'teiAdd',
            toolbar: 'tei-add'
        });

        // TEI-DELETE
        editor.addCommand( 'teiDelete', {
            exec: function( editor ) {
                var className = 'tei-del';
                var editorSelection = editor.getSelection();
                var range = editorSelection.getRanges()[ 0 ];
                var el = editor.document.createElement( 'div' );
                el.append(range.cloneContents());

                var commonAncestor = editorSelection.getCommonAncestor();
                if (className === commonAncestor.$.className || className === commonAncestor.$.parentElement.className) {
                    editor.insertHtml(el.getHtml());
                }
                else if (editorSelection.getSelectedText().length > 0) {
                    if (commonAncestor.$.className == 'tei-ins') {
                        range.deleteContents();
                    } 
                    var newElement = new CKEDITOR.dom.element("del");
                    newElement.setAttributes({class: className});
                    newElement.setHtml(el.getHtml());
                    var children = newElement.find('.'+className+', .tei-add, .tei-p');
                    for ( var i = 0; i < children.count(); i++ ) {
                        children.getItem( i ).$.outerHTML = children.getItem( i ).$.innerHTML;
                    }
                    editor.insertElement(newElement);
                }
                else {
                    return false;
                }
                var elements = editorSelection.document.getBody().getElementsByTag( '*' );
                for ( var i = 0; i < elements.count(); ++i ) {
                    if (elements.getItem(i).$.className !== 'tei-lb' && elements.getItem(i).$.innerHTML.length == 0) {
                        elements.getItem(i).remove();
                    } else if (elements.getItem(i).$.innerHTML == '<br class="tei-lb">') {
                        elements.getItem(i).$.outerHTML = elements.getItem(i).$.innerHTML;
                    }
                }
            }
        });
        editor.ui.addButton('TeiDel', {
            label: 'tei-del: highlights text that was\nmarked as deleted by an author',
            command: 'teiDelete',
            toolbar: 'tei-del'
        });

        // TEI-UNDERLINE
        editor.addCommand( 'teiUnderline', {
            exec: function( editor ) {
                var className = 'tei-hi';
                var editorSelection = editor.getSelection();
                var range = editorSelection.getRanges()[ 0 ];
                var el = editor.document.createElement( 'div' );
                el.append(range.cloneContents());

                var commonAncestor = editorSelection.getCommonAncestor();
                if (className === commonAncestor.$.className || className === commonAncestor.$.parentElement.className) {
                    editor.insertHtml(el.getHtml());
                }
                else if (editorSelection.getSelectedText().length > 0) {
                    var newElement = new CKEDITOR.dom.element("u");
                    newElement.setAttributes({class: className});
                    newElement.setAttributes({'data-tei-rend': 'underline'});
                    newElement.setHtml(el.getHtml());
                    var children = newElement.find('.'+className+', .tei-p');
                    for ( var i = 0; i < children.count(); i++ ) {
                        children.getItem( i ).$.outerHTML = children.getItem( i ).$.innerHTML;
                    }
                    editor.insertElement(newElement);
                }
                else {
                    return false;
                }
                var elements = editorSelection.document.getBody().getElementsByTag( '*' );
                for ( var i = 0; i < elements.count(); ++i ) {
                    if (elements.getItem(i).$.className !== 'tei-lb' && elements.getItem(i).$.innerHTML.length == 0) {
                        elements.getItem(i).remove();
                    } else if (elements.getItem(i).$.innerHTML == '<br class="tei-lb">') {
                        elements.getItem(i).$.outerHTML = elements.getItem(i).$.innerHTML;
                    }
                }
            }
        });
        editor.ui.addButton('TeiUnderline', {
            label: 'tei-hi: highlights text\nthat was underlined by an author',
            command: 'teiUnderline',
            toolbar: 'tei-underline'
        });

        // TEI-NOTE
        editor.addCommand( 'teiNote', {
            exec: function( editor ) {
                var className = 'tei-note';
                var editorSelection = editor.getSelection();
                var range = editorSelection.getRanges()[ 0 ];
                var el = editor.document.createElement( 'div' );
                el.append(range.cloneContents());

                var commonAncestor = editorSelection.getCommonAncestor();
                if (className === commonAncestor.$.className || className === commonAncestor.$.parentElement.className) {
                    editor.insertHtml(el.getHtml());
                }
                else if (editorSelection.getSelectedText().length > 0) {
                    var newElement = new CKEDITOR.dom.element("span");
                    newElement.setAttributes({class: className});
                    newElement.setHtml(el.getHtml());
                    var children = newElement.find('.'+className+', .tei-p');
                    for ( var i = 0; i < children.count(); i++ ) {
                        children.getItem( i ).$.outerHTML = children.getItem( i ).$.innerHTML;
                    }
                    editor.insertElement(newElement);
                }
                else {
                    return false;
                }
                var elements = editorSelection.document.getBody().getElementsByTag( '*' );
                for ( var i = 0; i < elements.count(); ++i ) {
                    if (elements.getItem(i).$.className !== 'tei-lb' && elements.getItem(i).$.innerHTML.length == 0) {
                        elements.getItem(i).remove();
                    } else if (elements.getItem(i).$.innerHTML == '<br class="tei-lb">') {
                        elements.getItem(i).$.outerHTML = elements.getItem(i).$.innerHTML;
                    }
                }
            }
        });
        editor.ui.addButton('TeiNote', {
            label: 'tei-note: inserts notes or\nannotations made by an author',
            command: 'teiNote',
            toolbar: 'tei-note'
        });

        // TEI-UNCLEAR
        editor.addCommand( 'teiUnclear', {
            exec: function( editor ) {
                var className = 'tei-unclear';
                var editorSelection = editor.getSelection();
                var range = editorSelection.getRanges()[ 0 ];
                var el = editor.document.createElement( 'div' );
                el.append(range.cloneContents());

                var commonAncestor = editorSelection.getCommonAncestor();
                var startTag = editorSelection.getStartElement();
                if (className === commonAncestor.$.className || className === commonAncestor.$.parentElement.className) {
                    editor.insertHtml(el.getHtml());
                }
                else if (editorSelection.getSelectedText().length > 0) {
                    var newElement = new CKEDITOR.dom.element("span");
                    newElement.setAttributes({class: className});
                    newElement.setHtml(el.getHtml());
                    var children = newElement.find('.'+className+', .tei-p');
                    for ( var i = 0; i < children.count(); i++ ) {
                        children.getItem( i ).$.outerHTML = children.getItem( i ).$.innerHTML;
                    }
                    editor.insertElement(newElement);
                }
                else {
                    return false;
                }
                var elements = editorSelection.document.getBody().getElementsByTag( '*' );
                for ( var i = 0; i < elements.count(); ++i ) {
                    if (elements.getItem(i).$.className !== 'tei-lb' && elements.getItem(i).$.innerHTML.length == 0) {
                        elements.getItem(i).remove();
                    } else if (elements.getItem(i).$.innerHTML == '<br class="tei-lb">') {
                        elements.getItem(i).$.outerHTML = elements.getItem(i).$.innerHTML;
                    }
                }
            }
        });
        editor.ui.addButton('TeiUnclear', {
            label: 'tei-unclear: highlights illegible text\nthat cannot be transcribed with certainty',
            command: 'teiUnclear',
            toolbar: 'tei-unclear'
        });

        // TEI-LINEBREAK
        editor.addCommand( 'teiLineBreak', {
            exec: function( editor ) {
                var className = 'tei-lb';
                var editorSelection = editor.getSelection();
                var range = editorSelection.getRanges()[ 0 ];
                var newElement = new CKEDITOR.dom.element("br");
                newElement.setAttributes({class: className});
                range.insertNode(newElement);
            }
        });
        editor.ui.addButton('TeiLineBreak', {
            label: 'tei-lb: inserts a line break',
            command: 'teiLineBreak',
            toolbar: 'tei-lb'
        });

        // TEI-PAGEBREAK
        editor.addCommand( 'teiPageBreak', {
            exec: function( editor ) {
                var className = 'tei-pb';
                var editorSelection = editor.getSelection();
                var range = editorSelection.getRanges()[ 0 ];
                var el = editor.document.createElement( 'div' );
                el.append(range.cloneContents());

                var commonAncestor = editorSelection.getCommonAncestor();
                var startTag = editorSelection.getStartElement();
                if (className === commonAncestor.$.parentElement.className) {
                    var html = commonAncestor.$.parentElement.innerHTML;
                    commonAncestor.remove();
                    editor.insertHtml(html);
                } 
                else if (className === startTag.$.className) {
                    var html = el.$.innerHTML;
                    var tag = "span";
                    var regexStart = new RegExp("<(?:(?!<).)*?"+ className +".*?>", 'gm');
                    var regexEnd = new RegExp("</"+tag+">", 'gm');
                    html = html.replace(regexStart, '');
                    html = html.replace(regexEnd, '');
                    editor.insertHtml(html);
                }
                else if (editorSelection.getSelectedText().length > 0) {
                    var newElement = new CKEDITOR.dom.element("span");
                    newElement.setAttributes({class: className});
                    newElement.setAttributes({'data-tei-n': editor.getSelection().getSelectedText()});
                    newElement.setHtml(el.getHtml());
                    var children = newElement.find('.'+className+', .tei-p');
                    for ( var i = 0; i < children.count(); i++ ) {
                        children.getItem( i ).$.outerHTML = children.getItem( i ).$.innerHTML;
                    }
                    editor.insertElement(newElement);
                }
                else {
                    return false;
                }
                var elements = editorSelection.document.getBody().getElementsByTag( '*' );
                for ( var i = 0; i < elements.count(); ++i ) {
                    if (elements.getItem(i).$.className !== 'tei-lb' && elements.getItem(i).$.innerHTML.length == 0) {
                        elements.getItem(i).remove();
                    } else if (elements.getItem(i).$.innerHTML == '<br class="tei-lb">') {
                        elements.getItem(i).$.outerHTML = elements.getItem(i).$.innerHTML;
                    }
                }
            }
        });
        editor.ui.addButton('TeiPageBreak', {
            label: 'tei-pb: marks the beginning of\na new page in a paginated document',
            command: 'teiPageBreak',
            toolbar: 'tei-pb'
        });

        // TEI-PARAGRAPH
        editor.addCommand( 'teiParagraph', {
            exec: function( editor ) {
                var className = 'tei-p';
                var editorSelection = editor.getSelection();
                var range = editorSelection.getRanges()[ 0 ];
                var el = editor.document.createElement( 'div' );
                el.append(range.cloneContents());

                var commonAncestor = editorSelection.getCommonAncestor();
                var startTag = editorSelection.getStartElement();
                if (className === commonAncestor.$.className) {
                    var html = commonAncestor.$.innerHTML;
                    commonAncestor.remove();
                    editor.insertHtml(html);
                }
                else if (className === startTag.$.className) {
                    startTag.remove();
                    editor.insertHtml(el.getHtml());
                }
                else if (editorSelection.getSelectedText().length > 0) {
                    var newElement = new CKEDITOR.dom.element("p");
                    newElement.setAttributes({class: className});
                    newElement.setHtml(el.getHtml());
                    var children = newElement.find('.'+className);
                    for ( var i = 0; i < children.count(); i++ ) {
                        children.getItem( i ).$.outerHTML = children.getItem( i ).$.innerHTML;
                    }
                    editor.insertElement(newElement);
                }
                else {
                    return false;
                }
                var elements = editorSelection.document.getBody().getElementsByTag( '*' );
                for ( var i = 0; i < elements.count(); ++i ) {
                    if (elements.getItem(i).$.className !== 'tei-lb' && elements.getItem(i).$.innerHTML.length == 0) {
                        elements.getItem(i).remove();
                    } else if (elements.getItem(i).$.innerHTML == '<br class="tei-lb">') {
                        elements.getItem(i).$.outerHTML = elements.getItem(i).$.innerHTML;
                    }
                }
            }
        });
        editor.ui.addButton('TeiParagraph', {
            label: 'tei-p: inserts a paragraph',
            command: 'teiParagraph',
            toolbar: 'tei-p'
        });

        // TODO - unwrap elements with only br in them
        // TODO - make sure that only markup relevant to the tag is removed, not all text markup - currently removing parents
    }
});
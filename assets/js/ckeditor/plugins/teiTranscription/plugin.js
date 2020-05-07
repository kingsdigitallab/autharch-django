
CKEDITOR.plugins.add( 'teiTranscription', {
    icons: 'teiPageBreak,teiAdd,teiDel,teiParagraph,teiLineBreak,teiNote,teiUnclear,teiUnderline',
    init: function( editor ) {

        // TEI-ADD
        editor.addCommand( 'teiAdd', {
            exec: function( editor ) {
                var className = 'tei-add';

                //get DOM object
                var editorSelection = editor.getSelection();
                //extract ranges of the selection
                var range = editorSelection.getRanges()[ 0 ];
                //create new DOM node
                var el = editor.document.createElement( 'div' );
                // insert a document fragment into a DOM
                el.append(range.cloneContents());

                //get a parent element of the selection to unwrap
                var commonAncestor = editorSelection.getCommonAncestor();
                //check class of the parent element; if the same as the class of the embedded icon, then unwrap
                if (className === commonAncestor.$.className) {
                    var html = commonAncestor.$.innerHTML;
                    commonAncestor.remove();
                    editor.insertHtml(html);
                } else {
                    //resolve a conflict with tei-del
                    /*
                        checks only the closest ancestor; 
                        therefore, if the text is wrapped in <del><u>text</u></del>, the condition is false
                    */
                    if (commonAncestor.$.className == 'tei-del') {
                        var html = commonAncestor.$.innerHTML;
                        commonAncestor.remove();
                    } 
                    var newElement = new CKEDITOR.dom.element("ins");
                    newElement.setAttributes({class: className});
                    newElement.setHtml(el.getHtml());
                    // check children - make sure the tag is not duplicated in inside the selected tag
                    var children = newElement.find('.'+className+', .tei-del');
                    for ( var i = 0; i < children.count(); i++ ) {
                        children.getItem( i ).$.outerHTML = children.getItem( i ).$.innerHTML;
                    }
                    editor.insertElement(newElement);
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
                if (className === commonAncestor.$.className) {
                    var html = commonAncestor.$.innerHTML;
                    commonAncestor.remove();
                    editor.insertHtml(html);
                } else {
                    if (commonAncestor.$.className == 'tei-add') {
                        var html = commonAncestor.$.innerHTML;
                        commonAncestor.remove();
                    } 
                    var newElement = new CKEDITOR.dom.element("del");
                    newElement.setAttributes({class: className});
                    newElement.setHtml(el.getHtml());
                    var children = newElement.find('.'+className+', .tei-add');
                    for ( var i = 0; i < children.count(); i++ ) {
                        children.getItem( i ).$.outerHTML = children.getItem( i ).$.innerHTML;
                    }
                    editor.insertElement(newElement);
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
                if (className === commonAncestor.$.className) {
                    var html = commonAncestor.$.innerHTML;
                    commonAncestor.remove();
                    editor.insertHtml(html);
                } else {
                    var newElement = new CKEDITOR.dom.element("u");
                    newElement.setAttributes({class: className});
                    newElement.setAttributes({'data-tei-rend': 'underline'});
                    newElement.setHtml(el.getHtml());
                    var children = newElement.find('.'+className);
                    for ( var i = 0; i < children.count(); i++ ) {
                        children.getItem( i ).$.outerHTML = children.getItem( i ).$.innerHTML;
                    }
                    editor.insertElement(newElement);
                }
            }
        });
        editor.ui.addButton('TeiUnderline', {
            label: 'tei-underline: highlights text\nthat was underlined by an author',
            command: 'teiUnderline',
            toolbar: 'tei-underline'
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
                if (className === commonAncestor.$.className || className === commonAncestor.$.parentElement.className) {
                    var html = commonAncestor.$.parentElement.innerHTML;
                    commonAncestor.remove();
                    editor.insertHtml(html);
                } else {
                    var newElement = new CKEDITOR.dom.element("span");
                    newElement.setAttributes({class: className});
                    newElement.setAttributes({'data-tei-n': editor.getSelection().getSelectedText()});
                    newElement.setHtml(el.getHtml());
                    var children = newElement.find('.'+className);
                    for ( var i = 0; i < children.count(); i++ ) {
                        children.getItem( i ).$.outerHTML = children.getItem( i ).$.innerHTML;
                    }
                    editor.insertElement(newElement);
                }
            }
        });
        editor.ui.addButton('TeiPageBreak', {
            label: 'tei-pb: marks the beginning of\na new page in a paginated document',
            command: 'teiPageBreak',
            toolbar: 'tei-pb'
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
                if (className === commonAncestor.$.className || className === commonAncestor.$.parentElement.className) {
                    var html = commonAncestor.$.innerHTML;
                    commonAncestor.remove();
                    editor.insertHtml(html);
                } else {
                    var newElement = new CKEDITOR.dom.element("span");
                    newElement.setAttributes({class: className});
                    newElement.setHtml(el.getHtml());
                    var children = newElement.find('.'+className);
                    for ( var i = 0; i < children.count(); i++ ) {
                        children.getItem( i ).$.outerHTML = children.getItem( i ).$.innerHTML;
                    }
                    editor.insertElement(newElement);
                }
            }
        });
        editor.ui.addButton('TeiUnclear', {
            label: 'tei-unclear: highlights illegible text\nthat cannot be transcribed with certainty',
            command: 'teiUnclear',
            toolbar: 'tei-unclear'
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
                if (className === commonAncestor.$.className) {
                    var html = commonAncestor.$.innerHTML;
                    commonAncestor.remove();
                    editor.insertHtml(html);
                } else {
                    var newElement = new CKEDITOR.dom.element("span");
                    newElement.setAttributes({class: className});
                    newElement.setHtml(el.getHtml());
                    var children = newElement.find('.'+className);
                    for ( var i = 0; i < children.count(); i++ ) {
                        children.getItem( i ).$.outerHTML = children.getItem( i ).$.innerHTML;
                    }
                    editor.insertElement(newElement);
                }
            }
        });
        editor.ui.addButton('TeiNote', {
            label: 'tei-note: inserts notes or\nannotations made by an author',
            command: 'teiNote',
            toolbar: 'tei-note'
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

        // TEI-PARAGRAPH
        // TODO - ensure paragraph is set as a parent element and wraps all TEI children
        editor.addCommand( 'teiParagraph', {
            exec: function( editor ) {
                var className = 'tei-p';
                var editorSelection = editor.getSelection();
                var range = editorSelection.getRanges()[ 0 ];
                var el = editor.document.createElement( 'div' );
                el.append(range.cloneContents());
                // TODO - ensure the 'p' element is broken down into the elements and content below the selection is wrapped into its own p tag
                var commonAncestor = editorSelection.getCommonAncestor();
                if (className === commonAncestor.$.className) {
                    var html = commonAncestor.$.innerHTML;
                    commonAncestor.remove();
                    editor.insertHtml(html);
                } else {
                    var newElement = new CKEDITOR.dom.element("p");
                    newElement.setAttributes({class: className});
                    newElement.setHtml(el.getHtml());
                    var children = newElement.find('.'+className);
                    for ( var i = 0; i < children.count(); i++ ) {
                        children.getItem( i ).$.outerHTML = children.getItem( i ).$.innerHTML;
                    }
                    editor.insertElement(newElement);
                }
            }
        });
        editor.ui.addButton('TeiParagraph', {
            label: 'tei-p: inserts a paragraph',
            command: 'teiParagraph',
            toolbar: 'tei-p'
        });

        // TODO - remove empty tags and tags with whitespace and type=_moz
        // TODO - make sure that only markup relevant to the tag is removed, not all text markup
    }
});
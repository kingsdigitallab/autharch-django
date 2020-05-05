
CKEDITOR.plugins.add( 'teiTranscription', {
    icons: 'teiAdd,teiDel',
    init: function( editor ) {
        editor.addCommand( 'insertTEIadd', {
            exec: function( editor ) {
                var className = 'tei-add';

                //get DOM object
                var editorSelection = editor.getSelection();
                //extract ranges of the selection
                var range = editorSelection.getRanges()[ 0 ];
                //create new DOM node
                var el = editor.document.createElement( 'div' );
                // copy selection and add it to a new DOM node
                el.append( range.cloneContents() );

                //get parent element of the selection to unwrap
                var startElement = editorSelection.getStartElement();

                //check class of the parent element; if the same as the class of the embedded icon, then unwrap
                if (className === startElement.$.className) {
                    var html = startElement.$.innerHTML;
                    editor.getSelection().getStartElement().remove();
                    editor.insertHtml(html);
                } else {
                    //create an element
                    var newElement = new CKEDITOR.dom.element("ins");
                    newElement.setAttributes({class: 'tei-add'});
                    newElement.setHtml(el.getHtml());
                    editor.insertElement(newElement);
                }
            }
        });
        editor.ui.addButton('TeiAdd', {
            label: 'insert tei-add',
            command: 'insertTEIadd',
            toolbar: 'tei-add'
        });

        editor.addCommand( 'insertTEIdelete', {
            exec: function( editor ) {
                var className = 'tei-del';

                //get DOM object
                var editorSelection = editor.getSelection();
                //extract ranges of the selection
                var range = editorSelection.getRanges()[ 0 ];
                //create new DOM node
                var el = editor.document.createElement( 'div' );
                // copy selection and add it to a new DOM node
                el.append( range.cloneContents() );

                //get parent element of the selection to unwrap
                var startElement = editorSelection.getStartElement();

                //check class of the parent element; if the same as the class of the embedded icon, then unwrap
                if (className === startElement.$.className) {
                    var html = startElement.$.innerHTML;
                    editor.getSelection().getStartElement().remove();
                    editor.insertHtml(html);
                } else {
                    //create an element
                    var newElement = new CKEDITOR.dom.element("del");
                    newElement.setAttributes({class: 'tei-del'});
                    newElement.setHtml(el.getHtml());
                    editor.insertElement(newElement);
                }
            }
        });
        editor.ui.addButton('TeiDel', {
            label: 'insert tei-del',
            command: 'insertTEIdelete',
            toolbar: 'tei-del'
        });
    }
});
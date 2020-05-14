/**
 * @license Copyright (c) 2003-2019, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see https://ckeditor.com/legal/ckeditor-oss-license
 */

CKEDITOR.editorConfig = function( config ) {
	// Define changes to default configuration here.
	// For complete reference see:
	// https://ckeditor.com/docs/ckeditor4/latest/api/CKEDITOR_config.html

	// The toolbar groups arrangement, optimized for a single toolbar row.
	config.toolbarGroups = [
		// { name: 'editing',     groups: [ 'find', 'selection', 'spellchecker' ] },
		// { name: 'forms' },
		// { name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
		// { name: 'paragraph',   groups: [ 'list', 'indent', 'blocks', 'align', 'bidi' ] },
		// { name: 'links' },
		// { name: 'insert' },
		{ name: 'tei-pb' },
		{ name: 'tei-p' },
		{ name: 'tei-underline' },
		{ name: 'tei-del' },
		{ name: 'tei-add' },
		{ name: 'tei-lb' },
		{ name: 'tei-note' },
		{ name: 'tei-unclear' },
		{ name: 'clipboard',   groups: [ 'clipboard', 'undo', 'redo' ] },
		{ name: 'document',	   groups: [ 'mode', 'document', 'doctools' ] },
	];
	config.allowedContent = true;
	config.extraPlugins = ['teiTranscription', 'sourcedialog'];
	// config.fillEmptyBlocks = false;
	// The default plugins included in the basic setup define some buttons that
	// are not needed in a basic editor. They are removed here.
	config.removeButtons = 'Cut,Copy,Paste,Anchor,Underline,Strike,Subscript,Superscript';

	// Dialog windows are also simplified.
	// config.removeDialogTabs = 'link:advanced';
};

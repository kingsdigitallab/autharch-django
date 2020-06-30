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
		{ name: 'tei-p' },
		{ name: 'tei-note' },
		{ name: 'tei-pb' },
		{ name: 'tei-underline' },
		{ name: 'tei-del' },
		{ name: 'tei-add' },
		{ name: 'tei-unclear' },
		{ name: 'tei-catchwords' },
		{ name: 'tei-foreign' },
		{ name: 'tei-formula' },
		{ name: 'tei-figure' },
		{ name: 'tei-lb' },
		{ name: 'tei-spaceBefore' },
		{ name: 'tei-spaceAfter' },
		{ name: 'document',	   groups: [ 'mode', 'document', 'doctools' ] },
		{ name: 'clipboard',   groups: [ 'clipboard', 'undo', 'redo' ] },
		{ name: 'tei-howToUse' },
	];
	config.allowedContent = true;
	CKEDITOR.timestamp = '10';
	config.extraPlugins = ['teiTranscription', 'sourcedialog', 'elementspath'];
	// The default plugins included in the basic setup define some buttons that
	// are not needed in a basic editor. They are removed here.
	config.removeButtons = 'Cut,Copy,Paste,Anchor,Underline,Strike,Subscript,Superscript';
	// Dialog windows are also simplified.
	// config.removeDialogTabs = 'link:advanced';
};
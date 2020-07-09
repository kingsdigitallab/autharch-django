# Help text for model fields. Note that any double quotes within these
# strings must be escaped as &quot; because they will occur within
# JavaScript strings.

CREATION_DATES_HELP = 'This element identifies and records the date(s) of creation of the records being described. The bulk of the records are within a certain period with only a few records of earlier or later date. In the latter case, if significant, reference should be made in the Description field. In the case of double-dating, the new style of date should be entered in the Date field. Add both the new style and old style of date in the Description field Square brackets should be used for derived dates. If there is any doubt as to the precise date, it can be preceded by &quot;?&quot; if the exact date is questionable or &quot;c.&quot;; if you are only able to narrow down the date range of the document by research. Some approximation of date should always be possible from the record relationship to other records in the series, office holders named, external events referred to, etc. The use of n.d. for undated should be avoided. If a document is undated, this can be noted in the Description field.'  # noqa

END_DATE_HELP = 'This element is used to identify the end date of the document(s). For Collection and Series levels, year dates should be used. For Sub-Series level and below, dates should include day and month (if known). Some approximation of date should always be possible from the record-relationship to other records in the series, office holders named, external events referred to, etc. <br><br>1. It is required that you follow the date format: <br><strong>(-)YYYY(-MM(-DD))</strong><br><em>e.g., 1822-03-27, 1822-03, 1822, or, if BC, -750.</em><br>2. To also assist with improving date searching, please always add a date range:<br><em>e.g., if the display date is 1822, include Start date: 1822, End date: 1822.</em><br><br>NB: Date ranges for years prior to the change in calendar may need to be taken into account. <br>NB: For dates spanning the change in calendars from Julian to Gregorian in many European countries and their colonies, include New Style dates for machine-reading. Old Style dates can be included in the display date field where needed.'  # noqa

START_DATE_HELP = 'This element is used to identify the start date of the document(s). For Collection and Series levels, year dates should be used. For Sub-Series level and below, dates should include day and month (if known). Some approximation of date should always be possible from the record-relationship to other records in the series, office holders named, external events referred to, etc. <br><br>1. It is required that you follow the date format: <br><strong>(-)YYYY(-MM(-DD))</strong><br><em>e.g., 1822-03-27, 1822-03, 1822, or, if BC, -750.</em><br>2. To also assist with improving date searching, please always add a date range:<br><em>e.g., if the display date is 1822, include Start date: 1822, End date: 1822.</em><br><br>NB: Date ranges for years prior to the change in calendar may need to be taken into account. <br>NB: For dates spanning the change in calendars from Julian to Gregorian in many European countries and their colonies, include New Style dates for machine-reading. Old Style dates can be included in the display date field where needed.'  # noqa

REFERENCES_HELP = 'This element is used for the Royal Archive, former and CALM references.'  # noqa

REPOSITORY_HELP = 'This element is used to give the managing custodian of the material being described. &quot;Royal Archives&quot; is the default content. Choose &quot;Royal Library&quot; when necessary.'  # noqa

# REPOSITORY_CODE_HELP = 'This element is used to give the ARCHON code for the institution holding the material. For the Georgian Papers Project, the Royal Library will be included under the umbrella of the Royal Archives ARCHON code.'  # noqa

RCIN_HELP = 'Royal Collection Inventory Number'

TITLE_HELP = 'This element is used to provide the name of the document(s) appropriate to the level of description. The title should normally not be longer than one sentence in length. If it is possible to summarise the whole document in the Title field then do so and omit use of the Description field. Dates should not normally be included in the Title field unless integral to the name of the record in question. At collection and series level, titles should provide a concise summary of the scope and content of the papers being described. In the case of letters, give the name of the writer and addressee. For those letters with a very clear sense of subject, this can be referred to briefly in the Title field. For those letters with a less clear subject (usually personal family letters which are very hard to summarise), the broad description &quot;on family matters&quot; should be used.'  # noqa

# CONTROL_HELP = 'This element encompasses administrative metadata.'

# CONTROL_LANGUAGE_HELP = 'The language and script of the EAC-CPF file (not for the entity itself).'  # noqa

RECORD_TYPE_HELP = 'This element is used to distinguish different types of record to enable users to filter searches to specific types of documents. This data element should be completed at the lowest level possible.'  # noqa

URL_HELP = 'This element is used to hold the URLs for the archival record in the Georgian Papers Online website, https://gpp.rct.uk/.'  # noqa

LOCATION_OF_ORIGINALS_HELP = 'This element is used to indicate the existence and location, availability and/or destruction of originals, if the unit of description consists of copies. If the original of the unit of description is available (either in the RA or elsewhere), its location should be recorded, together with any significant references. If the originals no longer exist, or their location is unknown, give that information.'  # noqa

RELATED_MATERIALS_LABEL_HELP = 'This element is used for the cross-referencing of relevant material held elsewhere in the Georgian Papers. Please include a descriptive label for the cross-referencing, e.g., &quot;For additional papers relating to Nathaniel Kent, see GEO/ADD/15/0356-0429&quot;'  # noqa

EXTENT_HELP = 'This element is used to give the number of records at the level being described. The extent of the record(s) should be given as appropriate to the level of description. This gives the user an idea of the size of a collection, series, item or file they are interested in. At higher levels, boxes can be included to help users visualise the size of the collection. At file and item levels, number of pages in the document(s) are required (in brackets) in order to guide users as to the size of the digital image download (PDF format). This should be ascertained at the cataloguing stage and not from the PDF. One letter equals one document regardless of length.'  # noqa

LANGUAGES_HELP = 'This element is used to give the language(s) in which the documents are written. English is the default content for this field. A new Language field should be created for each language entered. Prominence should be reflected, with the most heavily-used language being given first. At collection and series level the Language data element should give an indication of the most prominent language rather than every single language.'  # noqa

WRITER_HELP = 'This element is entered when the writer of the document can be identified. The name and title of the writer at the time of writing should be given. This data element will generally be used at File and Item level, but sometimes at Series level if the whole group of papers has been written by the same individual. If the writer cannot be identified, this data element should be left blank. Writers are those who own the intellectual content of a document, not the copyist. If the document has more than one writer, a new Writer field should be created for each name. Include life dates (in form 1765-1837) when necessary to differentiate between members of the royal family with the same name and title. Job title or occupation can be included if considered necessary, but is not mandatory. It is particularly useful for members of the Royal Household and tradespeople. Names and job titles should be separated by a semi-colon.'  # noqa

ADDRESSEE_HELP = 'This element is entered when the recipient of the document can be identified. The name and title of the addressee at the time of writing should be given. This data element will generally be used at File and Item level, but sometimes at Series level if the whole group of papers has been sent to the same individual. If the addressee cannot be identified, this data element should be left blank. If the document has more than one addressee, a new Addressee field should be created for each name. Include life dates (in form 1765-1837) when necessary to differentiate between members of the  royal family with the same name and title. Job title or occupation can be included if considered necessary, but is not mandatory. It is particular useful for members of the Royal Household and tradespeople. Names and job titles should be separated by a semi-colon.'  # noqa

PLACE_OF_WRITING_HELP = 'If the place of writing/receiving address is not available in the Geonames search, please include specific details in the record description.'

DESCRIPTION_HELP = 'This element is used to give a concise statement that describes the scope and content of the document(s), in particular what the material is and what it relates to. This should be a summary of the content of the document(s) appropriate and relevant to the level of description. This data element should include any issues with dates that cannot be expressed in the Dates field. For higher level records, metadata in the Description field can be itemised to reflect the content of the lower levels of the hierarchy. Content included in the Title field should not be repeated in the Description field. Thought should be given to subject keywords (people, places, events and topics) when entering the Description metadata. Quotations from the document(s) are acceptable in moderation, particularly if it is the only way to summarise the content of a document. Long transcripts should not be included. Record if a document is a copy or a draft or signed or unsigned in this data element. The time the document was signed can also be entered in the Description field. Any decorations, drawings or sketcheson the document can be noted here. Include cross-references to other documents in the collection in this field, for example when referring to enclosures and replies.'  # noqa

NOTES_HELP = 'This element is used to accommodate specialised information that cannot be entered in another data element. This field should only be used if there is information about the document(s) that cannot be accommodated in any of the other data elements.'  # noqa

PHYSICAL_DESCRIPTION_HELP = 'This element is used to describe the physical appearance of the document(s) and/or carriers, to aid visualisation by the user. Enter at the level at which the digitised image is attached. Provide a brief description of the physical attributes of the document(s) to help users visualise the original when viewing the digitised version.'  # noqa

ADMINISTRATIVE_HISTORY_HELP = 'This element is used to give the administrative history, biographical details or other historical information about the individual(s) or administrative body/bodies responsible for creating and accumulating the records being described. In the case of individuals, the Administrative History should include full names and titles, the life dates of the person, significant achievements and an outline of their career, concentrating on the period covered by the records in the series. The records of few administrative bodies are included in the Georgian Papers, but for those that are a summary of the organisation (or department) should include its title, purpose and function, and dates of existence as appropriate. It should be noted that the collections within the Georgian Papers are predominately artificial in creation and are based on records to, from and about an individual, rather than being records created by an individual. Some collections are also gathered together by type, and this should be reflected in the Administrative History. This data element should not be used for information about custodial history. Information entered in this data element should be pertinent to the creation of the particular collection of papers.'  # noqa

ARRANGEMENT_HELP = 'This element is used to provide information on the internal structure, order and/or system of classification of the unit of description. If the existing order of the papers has been preserved in cataloguing, this should be reflected in this data element. Re-arrangement of documents in the Georgian Papers is infrequent, but this data element should also be used to note any such re-arrangement or noteworthy points about the existing arrangement. At the top-level, a statement to note that &quot;this collection has been artificially created as part of the Georgian Papers digitisation and cataloguing programme&quot; should be included.'  # noqa

CUSTODIAL_HISTORY_PROVENANCE_HELP = 'This element is used to give information about the stewardship of papers prior to their accession to the Royal Archives. This data element should be used at whatever level it is appropriate to record custodial history information. Information on custodial history can often be found in the relevant accession record, but it is not always possible to ascertain how a collection entered the Royal Archives. If it is possible to ascertain that the collection entered the Royal Archives with the main deposit from Apsley House, this should be recorded. The name of donor and circumstances of the accession can be given, however it is not necessary to record the cost of the accession (at auction or otherwise). Information about Royal Household departments which reflect or affect the custodial history of the papers should also be included.'  # noqa

PUBLICATIONS_HELP = 'This element is used to identify any publications that are about or are based on the use or study of the document(s) in question. It is used to record a citation to, and/or information about, a publication that is about or based on the use or study of the unit of description, particularly transcriptions and references to published facsimiles. For the purposes of the Georgian Papers, this will predominately be the volumes edited by Aspinall, Fortescue, Namier and Donne.'  # noqa

COPYRIGHT_STATUS_HELP = 'This is an administrative field in which the copyright status of a document is given in order to inform the copyright clearance process for publication. This field should be completed at the level at which the digitised document is attached. It should be completed in conjunction with the internal document &quot;Guide to Copyright Categories&quot; for guidance as to which  option to choose from the picklist.'  # noqa

WITHHELD_HELP = 'This element is used to state when the digital image of a document(s) has been withheld from publication for copyright, conservation or other reasons. This field should be completed when the digital image of a document(s) cannot be published on Georgian Papers Online because copyright clearance has not been established or the document is too fragile to be digitised. It should be completed at the level at which the image should have been attached. This data element will typically be completed by the GPP Content Delivery Project Manager or the Archivist (Digital). If an item is missing, note in this data element.'  # noqa

CREDIT_HELP = 'This element is used to credit copyright holders who have given permission for material to be published online and require public acknowledgment. It should be completed when copyright holders have specifically requested a credit on Georgian Papers Online. it should also be completed at the level at which the image is attached. This data element will typically be completed by the GPP Content Delivery Project Manager or the Archivist (Digital) at the Royal Archives.' # noqa
/**
 * Public JavaScript objects for VF pages in Project1
 */
//Sfdc.ns("sforce.one");
//this.sforce = this.sforce || {};
(function(global) {
    // MUST BE INCREMENTED EVERY TIME A NEW COPY OF THIS FILE IS CREATED.
    // Should match the version directory it is contained in.
    var VERSION = "43.0";

    // Validation Method
    function isEntityId(value) {
        return Sfdc.isDefAndNotNull(value) && (value.length === 15 || value.length === 18);
    }

    // Versioned API the customer will end up getting.
    var s1 = {};

    /**
     * Executes one:back which goes back one step in the history. Also provides
     * the ability to refresh the page we are going back to.
     * @param {Boolean} refresh should the previous page refresh if possible.
     */
    s1.back = function(refresh) {
        if(Sfdc.isDefAndNotNull(refresh)) { Sfdc.assert(Sfdc.isBoolean(refresh), "sforce.one.back(refresh) - The refresh parameter is optional but when specified should be a boolean value indicating that you the page we are going back to should be refreshed."); }
        
        SfdcApp.projectOneNavigator.fireContainerEvent("one:back", { refresh: refresh } );
    };

    /**
     * Navigate to the sObject detail page. It has multiple views which are available as slides to specify.
     * 
     * @param {String} recordId Required parameter which is the recordId of the record you would like to view. Can be 15 or 18 characters.
     * @param {String} [view] Optional parameter to indicate which slide to view. Defaults to the detail view. Also available are related and chatter.
     */
    s1.navigateToSObject = function(recordId, view) {
        Sfdc.assert(isEntityId(recordId), "sforce.one.navigateToSObject(recordId, view) - RecordID is a required parameter and must be either 15 or 18 characters long.");
        if(Sfdc.isDefAndNotNull(view)) { Sfdc.assert(Sfdc.isString(view), "sforce.one.navigateToSObject(recordId, view) - view is an optional parameter but when specified should be done so as a string. The default available values are chatter, related and detail. With detail being the default."); }
        
        SfdcApp.projectOneNavigator.fireContainerEvent("force:navigateToSObject", { recordId: recordId, slideDevName: view} );
    };
    
    /**
     * Navigate to a specific URL. Internal to salesforce URL's will be loaded in an iframe if supported. 
     * Links with alternate prefixes like mailto and geo will try to do the appropriate thing.
     * 
     * @param {String} url Required parameter for which we plan to navigate to.
     * @param {Boolean} [isredirect] Optional parameter to indicate that the new page should take the old ones place in the browser history. 
     */
    s1.navigateToURL = function(url, isredirect) {
        Sfdc.assert(!Sfdc.isEmpty(url) && Sfdc.isString(url), "sforce.one.navigateToURL(url, isredirect) - url is a required parameter of type string indicating the location you would like to navigate to.");
        if(Sfdc.isDefAndNotNull(isredirect)) { Sfdc.assert(Sfdc.isBoolean(isredirect), "sforce.one.navigateToURL(url, isredirect) - isredirect is an optional parameter of boolean type indicating that the new page should take the old ones place in the browser history."); }
        
        SfdcApp.projectOneNavigator.fireContainerEvent("force:navigateToURL", { url: url, isredirect: isredirect } );
    };
    
    /**
     * Navigates to a specific feed. 
     * The SubjectID 
     * 
     *  @param {String} subjectId Varies based on the type of feed you are navigating. You'll want record id for records and topic id's for topics, otherwise you'll probably want a user id.
     *  @param {String} type Displays the various different feeds and thier states. Current possible values; NEWS, RECORD, TO, FILES, GROUPS, PEOPLE, BOOKMARKS, COMPANY and TOPICS. 
     */
    s1.navigateToFeed = function(subjectId, type) {
        Sfdc.assert(isEntityId(subjectId), "sforce.one.navigateToFeed(subjectId, type) - subjectId is a required parameter of type string that indicates the record ID of the entity whos feed you would like to view.");
        Sfdc.assert(Sfdc.isString(type), "sforce.one.navigateToFeed(subjectId, type) - type is a required parameter of type String that is the Feed type you are trying to display.  Current possible values; NEWS, RECORD, TO, FILES, GROUPS, PEOPLE, BOOKMARKS, COMPANY and TOPICS.");
        Sfdc.assert(type === type.toUpperCase(), "sforce.one.navigateToFeed(subjectId, type) - type must be all uppercase letters.  Current possible values; NEWS, RECORD, TO, FILES, GROUPS, PEOPLE, BOOKMARKS, COMPANY and TOPICS.");

        SfdcApp.projectOneNavigator.fireContainerEvent("force:navigateToFeed", { subjectId: subjectId, type: type } );
    };
    
    /**
     * Navigate to a specific feed item with its accompanying comments.
     * 
     * @param {String} feedItemId The id of the specific feed item to load.
     */
    s1.navigateToFeedItemDetail = function(feedItemId) {
        Sfdc.assert(isEntityId(feedItemId), "sforce.one.navigateToFeedItemDetail(feedItemId) - feedItemId is a required parameter of type string indicating the feed item to drill into.");
        
        SfdcApp.projectOneNavigator.fireContainerEvent("force:navigateToFeedItemDetail", { feedItemId: feedItemId } );
    };
    
    /**
     * Navigate to the view that shows all the items in a particular related list.
     * 
     * @param {String} relatedListId For standard lists, we use the format Related[Entity]List such as RelatedContactList or RelatedAccountList. For custom lists, you'll need to use the ID of the related list.
     * @param {String} parentRecordId The actual id of the entity for which to query the data for the related list.
     */
    s1.navigateToRelatedList = function(relatedListId, parentRecordId) {
        Sfdc.assert(Sfdc.isString(relatedListId), "sforce.one.navigateToRelatedList(relatedListId, parentRecordId) - relatedListId is a required value of type String. For standard lists, we use the format Related[Entity]List such as RelatedContactList or RelatedAccountList. For custom lists, you'll need to use the ID of the related list.");
        Sfdc.assert(isEntityId(parentRecordId), "sforce.one.navigateToRelatedList(relatedListId, parentRecordId) - parentRecordId is a required value and should be an id of 15 or 18 characters long. The actual id of the entity for which to query the data for the related list.");

        SfdcApp.projectOneNavigator.fireContainerEvent("force:navigateToRelatedList", { relatedListId: relatedListId, parentRecordId: parentRecordId } );
    };
    
    /**
     * Navigate to the List of entities.
     * 
     * @param {String} listViewId The unique ID of the listView you wish to display.
     * @param {String} listViewName Title of the ListView you are intending to display, does not need to match the name of the ListView saved in the database.
     * @param {String} scope Is the entity name associated with this listView. If it is a list of Accounts then "Account", Custom objects of type color, then "Color__c".
     */
    s1.navigateToList = function(listViewId, listViewName, scope) {
        Sfdc.assert(isEntityId(listViewId), "sforce.one.navigateToList(listViewId, listViewName, scope) - listViewId is a required parameter of length 15 to 18 characters. Which is the unique ID of the listView you wish to display.");
        Sfdc.assert(Sfdc.isString(scope), "sforce.one.navigateToList(listViewId, listViewName, scope) - scope is a required parameter of type string. It is the entity name associated with this listView. If it is a list of Accounts then 'Account', Custom objects of type color, then 'Color__c'.");
        if(Sfdc.isDefAndNotNull(listViewName)) { Sfdc.assert(Sfdc.isString(listViewName), "sforce.one.navigateToList(listViewId, listViewName, scope) - listViewName is optional but when supplied should be done so as a string. It shows up at the top of the list as the primary header of the list."); }
        
        SfdcApp.projectOneNavigator.fireContainerEvent("force:navigateToList", { listViewId: listViewId, listViewName: listViewName, scope: scope } );
    };
    
    /**
     * Navigate to an entity
     * 
     * @param {String} scope The standard or custom object entity name or key prefix to navigate to
     */
    s1.navigateToObjectHome = function(scope) {
        Sfdc.assert(Sfdc.isString(scope), "sforce.one.navigateToObjectHome(scope) - scope is a required parameter of type string. It should be the entity name or key prefix of a standard or custom object");
        
        SfdcApp.projectOneNavigator.fireContainerEvent("force:navigateToObjectHome", { scope: scope } );
    };
    
    /**
     * Launch the create a new entity screen.
     * 
     * @param {String} entityName Entity name in the API, such as Account, Contact, CustomObject__c.
     * @param {String} recordTypeId Only used When record types are setup for the organization.
     * @param {String} defaultFieldValues An object with key-value pairs of fields and values to prepopulate.
     */
    s1.createRecord = function(entityName, recordTypeId, defaultFieldValues) {
        Sfdc.assert(Sfdc.isString(entityName), "sforce.one.createRecord(entityName, recordTypeId, defaultFieldValues) - entityName is a required parameter of type String. It should match the entity name in the API, such as Account, Contact, CustomObject__c.");
        if(Sfdc.isDefAndNotNull(recordTypeId)) { Sfdc.assert(isEntityId(recordTypeId), "sforce.one.createRecord(entityName, recordTypeId, defaultFieldValues) - recordTypeId is an optional parameter but when specified should be an id of length 15 or 18. This should be the ID of the record type."); }
        if(Sfdc.isDefAndNotNull(defaultFieldValues)) { Sfdc.assert(Sfdc.isObject(defaultFieldValues), 'sforce.one.createRecord(entityName, recordTypeId, defaultFieldValues) - defaultFieldValues is an optional parameter of type Object. It allows prepopulation of fields on new record. {Phone: 1112223333, Name: "Salesforce"}'); }
        SfdcApp.projectOneNavigator.fireContainerEvent("force:createRecord", { entityApiName: entityName, recordTypeId: recordTypeId, defaultFieldValues: defaultFieldValues } );
    };
    
    /**
     * Launch the edit screen for the specified entity.
     *
     * @param {String} recordId The entity ID for record you wish to edit.
     */
    s1.editRecord = function(recordId) {
        Sfdc.assert(isEntityId(recordId), "sforce.one.editRecord(recordId) - recordId is a required parameter in the form of an id with length 15 or 18 characters. It is simply the ID of the entity you wish to edit.");

        SfdcApp.projectOneNavigator.fireContainerEvent("force:editRecord", { recordId: recordId } );
    };
    
    // s1.showQuickAction = function() {
 //     // NOT IMPLEMENTED - parameters are not api complete Sfdc.Salesforce1_Internal.fireContainerEvent("force:showQuickAction", { } );
    // };
    
    // s1.navigateToCanvasApp = function() {
 //     // NOT IMPLEMENTED - parameters incomplete in function Sfdc.Salesforce1_Internal.fireContainerEvent("force:navigateToCanvasApp", { } );
    // };
    
    //return s1;

    // DO NOT CHANGE THE SIGNATURE. 
    // Sfdc.define() will error if different signatures are passed. 
    // If you do need to change the signature of this method (doubt it)
    // then you'll need to change them all. 
    Sfdc.define("sforce/one/*", function(){return s1;}); 
    // Specify the individual version
    Sfdc.define("sforce/one/version/"+VERSION, function(){return s1;});
})(this);

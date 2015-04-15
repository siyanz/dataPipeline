function myFunction(){ 
  // Open a form by ID and create a new spreadsheet.
   var form = FormApp.create('test');
   var ss = SpreadsheetApp.openById('1htrYVw9MMfDol4ExLXLxvcC7UDzALSsgHQcbSKhWEiM');
  
   // Update form properties via chaining.
   form.setTitle('ISIS Twitter Network Handle Classification ')
       .setDescription('Description of form')
       .setConfirmationMessage('Thanks for responding!')
       .setAllowResponseEdits(true)
       .setAcceptingResponses(true);
  
  form.addGridItem()
    .setTitle('Categorize these twitter handles')
    .setRows(['id1', 'id2', 'id3'])
    .setColumns(['Propagandist', 'News Media', 'Neither']);
  
   form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());
};
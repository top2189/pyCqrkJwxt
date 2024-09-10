$(function(){
     $(document).on('click', '#guide', function() {
         $(this).toggleClass('toggled');
         $('#sidebar').toggleClass('toggled');
     });
});
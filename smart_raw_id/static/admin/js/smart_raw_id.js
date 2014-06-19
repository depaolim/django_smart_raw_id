(function($) {
  $(document).ready(function($) {
    var update_label = (function() {
      var $this = $(this), url = $this.data('wsu');
      var name = this.id;/*.replace("id_", "");*/
      var multi = $this.hasClass("vManyToManyRawIdAdminField");
      var value = $this.val();

      try {
        // only fire the ajax call if we have all the required info
        if ((url !== undefined) && (value !== undefined) && (value !== "")) {
          $.ajax({
            url: url,
            data: {"pk": value},
            success: function(data){
              var lbl = $("#lbl_" + name);
              lbl.html(" " + data);
              if ($this.data('suggested') == value) {
                lbl.addClass('suggested');
              } else {
                lbl.removeClass('suggested');
              }
            }
          });
        } else if (value == "") {
          $("#lbl_" + name).html(" ");
        }
      } catch (e) {
        if (window.console) {
          console.log("raw_id_fields: " + e);
        }
      }
    });

    var reset_raw_id = function() {
      $("#" + this.id.substr(4)).val('').trigger('change');
      return false;
    };

    $(".vForeignKeyRawIdAdminField, .vManyToManyRawIdAdminField").hide().each(function(){
      var par = $("#lookup_" + this.id).parent(), lbl = "lbl_" + this.id, clr = "clr_" + this.id;
      var help = par.children(".help").remove();
      if (par.find(lbl).length == 0) {
        par.append('<span class="fk-tag" id="' + lbl + '"></span>');
      }
      if (par.find(clr).length == 0) {
        par.append('<a class="deletelink" href="#" id="' + clr + '">&nbsp;</a>');
        $("#" + clr).click(reset_raw_id);
      }
      par.append(help);
      this.update_label = update_label;
    }).change(function(e){
      if (!this.update_label) {
          this.update_label = update_label;
      }
      this.update_label();
      //e.stopPropagation();
    });

    $(".vManyToManyRawIdAdminField").trigger('change');
    $(".vForeignKeyRawIdAdminField").trigger('change');
    if (!window._dismissRelatedLookupPopup && window.dismissRelatedLookupPopup) {
      window._dismissRelatedLookupPopup = window.dismissRelatedLookupPopup;
      window.dismissRelatedLookupPopup = function(win, chosenId) {
        window._dismissRelatedLookupPopup(win, chosenId);
        $(document.getElementById(windowname_to_id(win.name))).trigger('change');
      }
    }
    else alert("no dismiss");
  });
})(django.jQuery);

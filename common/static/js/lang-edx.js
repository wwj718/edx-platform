var edx = edx || {},
    Language = (function($) {
        'use strict';
        var preference_api_url = $('#preference-api-url').val(),
            settings_language_selector = $('#settings-language-value'),
            self = null;
        return {

            init: function() {
                self = this;
                this.listenForLanguagePreferenceChange();
            },

            /**
             * Listener on changing language from selector.
             * Send an ajax request to save user language preferences.
             */
            listenForLanguagePreferenceChange: function() {
                settings_language_selector.change(function(event) {
                    event.preventDefault();

                    // ajax request to save user language preferences.
                    self.sendAjaxRequest(preference_api_url, this.value, function () {

                        // User language preference has been set successfully
                        // Now submit the form in success callback.
                        $("#language-settings-form").submit();
                    });
                });
            },

            /**
             * Send an ajax request to save user language preferences.
             */
            sendAjaxRequest: function(url, language, callback) {
                // ajax request to save user language preferences.
                $.ajax({
                    type: 'PATCH',
                    data:JSON.stringify({'pref-lang': language}) ,
                    url: url,
                    dataType: 'json',
                    contentType: "application/merge-patch+json",
                    beforeSend: function (xhr) {
                        xhr.setRequestHeader("X-CSRFToken", $('#csrf_token').val());
                    },
                    success: function () {
                        callback();
                    },
                    error: function () {
                        this.refresh();
                    }
                });
            },

            /**
             * refresh the page.
             */
            refresh: function () {
                document.location.reload();
            }

        };
    })(jQuery);

Language.init();

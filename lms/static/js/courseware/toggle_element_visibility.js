;(function (define) {
    'use strict';

    define(['jquery', 'logger', 'moment'],
        function ($, Logger, moment) {

            return function () {
                // define variables for code legibility
                var toggleActionElements = $('.toggle-visibility-button');

                var updateToggleActionText = function (hideElement, actionElement) {
                    var show_text = actionElement.data('show');
                    var hide_text = actionElement.data('hide');

                    if (hideElement) {
                        if (hide_text) {
                            actionElement.html(actionElement.data('hide'));
                        } else {
                            actionElement.hide();
                        }
                    } else {
                        if (show_text) {
                            actionElement.html(actionElement.data('show'));
                        }
                    }
                };

                $.each(toggleActionElements, function (i, elem) {
                    var toggleActionElement = $(elem),
                        toggleTargetElement = toggleActionElement.siblings('.toggle-visibility-element'),
                        hideElement = toggleTargetElement.is(':visible'),
                        date = toggleTargetElement.siblings('.date').text();

                    updateToggleActionText(toggleTargetElement, toggleActionElement);

                    toggleActionElement.on('click', function (event) {
                        event.preventDefault();
                        toggleTargetElement.toggleClass('hidden');
                        updateToggleActionText(toggleTargetElement, toggleActionElement);
                        Logger.log('edx.course.home.update_toggled', {
                            action: hideElement ? 'hide' : 'show',
                            date: moment(date, 'MMM DD, YYYY').format()
                        });
                    });
                });
            };
        });
})(define || RequireJS.define);

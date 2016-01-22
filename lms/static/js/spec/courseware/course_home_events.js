define(['jquery', 'logger', 'js/courseware/course_home_events'], function ($, Logger, courseHomeEvents) {
    'use strict';

    describe('Course home page eventing', function () {
        beforeEach(function () {
            loadFixtures('js/fixtures/courseware/course_home_events.html');
            courseHomeEvents();
            spyOn(Logger, 'log');
        });

        it('sends an event when "Resume Course" is clicked', function () {
            $('.last-accessed-link').click();
            expect(Logger.log).toHaveBeenCalledWith('edx.course.home.resume_course.clicked', {});
        });

        it('sends an event when "Upgrade to Verified" is clicked', function () {
            $('.date-summary-link').click();
            expect(Logger.log).toHaveBeenCalledWith('edx.course.home.upgrade_verified.clicked', {});
        });
    });
});

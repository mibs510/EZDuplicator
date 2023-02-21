"""

Copyright (c) 2022 Connor McMillan <connor@mcmillan.website>. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

"""
import logging
import os
import sys
from pathlib import Path

from gi import require_version as gi_require_version
from gi.repository import Gtk

import EZDuplicator.lib.DataOnlyDuplication
import EZDuplicator.lib.EZDuplicator
import EZDuplicator.lib.QA

gi_require_version('Gtk', '3.0')


class CapacityDetailsDialog(Gtk.Dialog):
    """ Main window with all components. """

    def __init__(self):
        Gtk.Dialog.__init__(self)
        self.builder = Gtk.Builder()
        gladefile = str(Path(__file__).parent.absolute()) + '/res/window.ui'
        if not os.path.exists(gladefile):
            # Look for glade file in this project's directory.
            gladefile = os.path.join(sys.path[0], gladefile)

        try:
            self.builder.add_objects_from_file(
                gladefile,
                [
                    'CapacityDetailsDialog',
                    'CapacityDetailsDialog_Close',
                    'CapacityDetailsDialog_Msg',
                    'CapacityDetailsDialog_SourceCapacity',
                    'CapacityDetailsDialog_SourceImage',
                    'CapacityDetailsDialog_Title',
                    'CapacityDetailsDialog_eight_five_Capacity',
                    'CapacityDetailsDialog_eight_five_Image',
                    'CapacityDetailsDialog_eight_four_Capacity',
                    'CapacityDetailsDialog_eight_four_Image',
                    'CapacityDetailsDialog_eight_one_Capacity',
                    'CapacityDetailsDialog_eight_one_Image',
                    'CapacityDetailsDialog_eight_seven_Capacity',
                    'CapacityDetailsDialog_eight_seven_Image',
                    'CapacityDetailsDialog_eight_six_Capacity',
                    'CapacityDetailsDialog_eight_six_Image',
                    'CapacityDetailsDialog_eight_three_Capacity',
                    'CapacityDetailsDialog_eight_three_Image',
                    'CapacityDetailsDialog_eight_two_Capacity',
                    'CapacityDetailsDialog_eight_two_Image',
                    'CapacityDetailsDialog_eight_zero_Capacity',
                    'CapacityDetailsDialog_eight_zero_Image',
                    'CapacityDetailsDialog_eleven_five_Capacity',
                    'CapacityDetailsDialog_eleven_five_Image',
                    'CapacityDetailsDialog_eleven_four_Capacity',
                    'CapacityDetailsDialog_eleven_four_Image',
                    'CapacityDetailsDialog_eleven_one_Capacity',
                    'CapacityDetailsDialog_eleven_one_Image',
                    'CapacityDetailsDialog_eleven_seven_Capacity',
                    'CapacityDetailsDialog_eleven_seven_Image',
                    'CapacityDetailsDialog_eleven_six_Capacity',
                    'CapacityDetailsDialog_eleven_six_Image',
                    'CapacityDetailsDialog_eleven_three_Capacity',
                    'CapacityDetailsDialog_eleven_three_Image',
                    'CapacityDetailsDialog_eleven_two_Capacity',
                    'CapacityDetailsDialog_eleven_two_Image',
                    'CapacityDetailsDialog_eleven_zero_Capacity',
                    'CapacityDetailsDialog_eleven_zero_Image',
                    'CapacityDetailsDialog_fifteen_five_Capacity',
                    'CapacityDetailsDialog_fifteen_five_Image',
                    'CapacityDetailsDialog_fifteen_four_Capacity',
                    'CapacityDetailsDialog_fifteen_four_Image',
                    'CapacityDetailsDialog_fifteen_one_Capacity',
                    'CapacityDetailsDialog_fifteen_one_Image',
                    'CapacityDetailsDialog_fifteen_seven_Capacity',
                    'CapacityDetailsDialog_fifteen_seven_Image',
                    'CapacityDetailsDialog_fifteen_six_Capacity',
                    'CapacityDetailsDialog_fifteen_six_Image',
                    'CapacityDetailsDialog_fifteen_three_Capacity',
                    'CapacityDetailsDialog_fifteen_three_Image',
                    'CapacityDetailsDialog_fifteen_two_Capacity',
                    'CapacityDetailsDialog_fifteen_two_Image',
                    'CapacityDetailsDialog_fifteen_zero_Capacity',
                    'CapacityDetailsDialog_fifteen_zero_Image',
                    'CapacityDetailsDialog_five_five_Capacity',
                    'CapacityDetailsDialog_five_five_Image',
                    'CapacityDetailsDialog_five_four_Capacity',
                    'CapacityDetailsDialog_five_four_Image',
                    'CapacityDetailsDialog_five_one_Capacity',
                    'CapacityDetailsDialog_five_one_Image',
                    'CapacityDetailsDialog_five_seven_Capacity',
                    'CapacityDetailsDialog_five_seven_Image',
                    'CapacityDetailsDialog_five_six_Capacity',
                    'CapacityDetailsDialog_five_six_Image',
                    'CapacityDetailsDialog_five_three_Capacity',
                    'CapacityDetailsDialog_five_three_Image',
                    'CapacityDetailsDialog_five_two_Capacity',
                    'CapacityDetailsDialog_five_two_Image',
                    'CapacityDetailsDialog_five_zero_Capacity',
                    'CapacityDetailsDialog_five_zero_Image',
                    'CapacityDetailsDialog_four_five_Capacity',
                    'CapacityDetailsDialog_four_five_Image',
                    'CapacityDetailsDialog_four_four_Capacity',
                    'CapacityDetailsDialog_four_four_Image',
                    'CapacityDetailsDialog_four_one_Capacity',
                    'CapacityDetailsDialog_four_one_Image',
                    'CapacityDetailsDialog_four_seven_Capacity',
                    'CapacityDetailsDialog_four_seven_Image',
                    'CapacityDetailsDialog_four_six_Capacity',
                    'CapacityDetailsDialog_four_six_Image',
                    'CapacityDetailsDialog_four_three_Capacity',
                    'CapacityDetailsDialog_four_three_Image',
                    'CapacityDetailsDialog_four_two_Capacity',
                    'CapacityDetailsDialog_four_two_Image',
                    'CapacityDetailsDialog_four_zero_Capacity',
                    'CapacityDetailsDialog_four_zero_Image',
                    'CapacityDetailsDialog_fourteen_five_Capacity',
                    'CapacityDetailsDialog_fourteen_five_Image',
                    'CapacityDetailsDialog_fourteen_four_Capacity',
                    'CapacityDetailsDialog_fourteen_four_Image',
                    'CapacityDetailsDialog_fourteen_one_Capacity',
                    'CapacityDetailsDialog_fourteen_one_Image',
                    'CapacityDetailsDialog_fourteen_seven_Capacity',
                    'CapacityDetailsDialog_fourteen_seven_Image',
                    'CapacityDetailsDialog_fourteen_six_Capacity',
                    'CapacityDetailsDialog_fourteen_six_Image',
                    'CapacityDetailsDialog_fourteen_three_Capacity',
                    'CapacityDetailsDialog_fourteen_three_Image',
                    'CapacityDetailsDialog_fourteen_two_Capacity',
                    'CapacityDetailsDialog_fourteen_two_Image',
                    'CapacityDetailsDialog_fourteen_zero_Capacity',
                    'CapacityDetailsDialog_fourteen_zero_Image',
                    'CapacityDetailsDialog_nine_five_Capacity',
                    'CapacityDetailsDialog_nine_five_Image',
                    'CapacityDetailsDialog_nine_four_Capacity',
                    'CapacityDetailsDialog_nine_four_Image',
                    'CapacityDetailsDialog_nine_one_Capacity',
                    'CapacityDetailsDialog_nine_one_Image',
                    'CapacityDetailsDialog_nine_seven_Capacity',
                    'CapacityDetailsDialog_nine_seven_Image',
                    'CapacityDetailsDialog_nine_six_Capacity',
                    'CapacityDetailsDialog_nine_six_Image',
                    'CapacityDetailsDialog_nine_three_Capacity',
                    'CapacityDetailsDialog_nine_three_Image',
                    'CapacityDetailsDialog_nine_two_Capacity',
                    'CapacityDetailsDialog_nine_two_Image',
                    'CapacityDetailsDialog_nine_zero_Capacity',
                    'CapacityDetailsDialog_nine_zero_Image',
                    'CapacityDetailsDialog_one_five_Capacity',
                    'CapacityDetailsDialog_one_five_Image',
                    'CapacityDetailsDialog_one_four_Capacity',
                    'CapacityDetailsDialog_one_four_Image',
                    'CapacityDetailsDialog_one_one_Capacity',
                    'CapacityDetailsDialog_one_one_Image',
                    'CapacityDetailsDialog_one_seven_Capacity',
                    'CapacityDetailsDialog_one_seven_Image',
                    'CapacityDetailsDialog_one_six_Capacity',
                    'CapacityDetailsDialog_one_six_Image',
                    'CapacityDetailsDialog_one_three_Capacity',
                    'CapacityDetailsDialog_one_three_Image',
                    'CapacityDetailsDialog_one_two_Capacity',
                    'CapacityDetailsDialog_one_two_Image',
                    'CapacityDetailsDialog_one_zero_Capacity',
                    'CapacityDetailsDialog_one_zero_Image',
                    'CapacityDetailsDialog_seven_five_Capacity',
                    'CapacityDetailsDialog_seven_five_Image',
                    'CapacityDetailsDialog_seven_four_Capacity',
                    'CapacityDetailsDialog_seven_four_Image',
                    'CapacityDetailsDialog_seven_one_Capacity',
                    'CapacityDetailsDialog_seven_one_Image',
                    'CapacityDetailsDialog_seven_seven_Capacity',
                    'CapacityDetailsDialog_seven_seven_Image',
                    'CapacityDetailsDialog_seven_six_Capacity',
                    'CapacityDetailsDialog_seven_six_Image',
                    'CapacityDetailsDialog_seven_three_Capacity',
                    'CapacityDetailsDialog_seven_three_Image',
                    'CapacityDetailsDialog_seven_two_Capacity',
                    'CapacityDetailsDialog_seven_two_Image',
                    'CapacityDetailsDialog_seven_zero_Capacity',
                    'CapacityDetailsDialog_seven_zero_Image',
                    'CapacityDetailsDialog_six_five_Capacity',
                    'CapacityDetailsDialog_six_five_Image',
                    'CapacityDetailsDialog_six_four_Capacity',
                    'CapacityDetailsDialog_six_four_Image',
                    'CapacityDetailsDialog_six_one_Capacity',
                    'CapacityDetailsDialog_six_one_Image',
                    'CapacityDetailsDialog_six_seven_Capacity',
                    'CapacityDetailsDialog_six_seven_Image',
                    'CapacityDetailsDialog_six_six_Capacity',
                    'CapacityDetailsDialog_six_six_Image',
                    'CapacityDetailsDialog_six_three_Capacity',
                    'CapacityDetailsDialog_six_three_Image',
                    'CapacityDetailsDialog_six_two_Capacity',
                    'CapacityDetailsDialog_six_two_Image',
                    'CapacityDetailsDialog_six_zero_Capacity',
                    'CapacityDetailsDialog_six_zero_Image',
                    'CapacityDetailsDialog_ten_five_Capacity',
                    'CapacityDetailsDialog_ten_five_Image',
                    'CapacityDetailsDialog_ten_four_Capacity',
                    'CapacityDetailsDialog_ten_four_Image',
                    'CapacityDetailsDialog_ten_one_Capacity',
                    'CapacityDetailsDialog_ten_one_Image',
                    'CapacityDetailsDialog_ten_seven_Capacity',
                    'CapacityDetailsDialog_ten_seven_Image',
                    'CapacityDetailsDialog_ten_six_Capacity',
                    'CapacityDetailsDialog_ten_six_Image',
                    'CapacityDetailsDialog_ten_three_Capacity',
                    'CapacityDetailsDialog_ten_three_Image',
                    'CapacityDetailsDialog_ten_two_Capacity',
                    'CapacityDetailsDialog_ten_two_Image',
                    'CapacityDetailsDialog_ten_zero_Capacity',
                    'CapacityDetailsDialog_ten_zero_Image',
                    'CapacityDetailsDialog_thirteen_five_Capacity',
                    'CapacityDetailsDialog_thirteen_five_Image',
                    'CapacityDetailsDialog_thirteen_four_Capacity',
                    'CapacityDetailsDialog_thirteen_four_Image',
                    'CapacityDetailsDialog_thirteen_one_Capacity',
                    'CapacityDetailsDialog_thirteen_one_Image',
                    'CapacityDetailsDialog_thirteen_seven_Capacity',
                    'CapacityDetailsDialog_thirteen_seven_Image',
                    'CapacityDetailsDialog_thirteen_six_Capacity',
                    'CapacityDetailsDialog_thirteen_six_Image',
                    'CapacityDetailsDialog_thirteen_three_Capacity',
                    'CapacityDetailsDialog_thirteen_three_Image',
                    'CapacityDetailsDialog_thirteen_two_Capacity',
                    'CapacityDetailsDialog_thirteen_two_Image',
                    'CapacityDetailsDialog_thirteen_zero_Capacity',
                    'CapacityDetailsDialog_thirteen_zero_Image',
                    'CapacityDetailsDialog_three_five_Capacity',
                    'CapacityDetailsDialog_three_five_Image',
                    'CapacityDetailsDialog_three_four_Capacity',
                    'CapacityDetailsDialog_three_four_Image',
                    'CapacityDetailsDialog_three_one_Capacity',
                    'CapacityDetailsDialog_three_one_Image',
                    'CapacityDetailsDialog_three_seven_Capacity',
                    'CapacityDetailsDialog_three_seven_Image',
                    'CapacityDetailsDialog_three_six_Capacity',
                    'CapacityDetailsDialog_three_six_Image',
                    'CapacityDetailsDialog_three_three_Capacity',
                    'CapacityDetailsDialog_three_three_Image',
                    'CapacityDetailsDialog_three_two_Capacity',
                    'CapacityDetailsDialog_three_two_Image',
                    'CapacityDetailsDialog_three_zero_Capacity',
                    'CapacityDetailsDialog_three_zero_Image',
                    'CapacityDetailsDialog_twelve_five_Capacity',
                    'CapacityDetailsDialog_twelve_five_Image',
                    'CapacityDetailsDialog_twelve_four_Capacity',
                    'CapacityDetailsDialog_twelve_four_Image',
                    'CapacityDetailsDialog_twelve_one_Capacity',
                    'CapacityDetailsDialog_twelve_one_Image',
                    'CapacityDetailsDialog_twelve_seven_Capacity',
                    'CapacityDetailsDialog_twelve_seven_Image',
                    'CapacityDetailsDialog_twelve_six_Capacity',
                    'CapacityDetailsDialog_twelve_six_Image',
                    'CapacityDetailsDialog_twelve_three_Capacity',
                    'CapacityDetailsDialog_twelve_three_Image',
                    'CapacityDetailsDialog_twelve_two_Capacity',
                    'CapacityDetailsDialog_twelve_two_Image',
                    'CapacityDetailsDialog_twelve_zero_Capacity',
                    'CapacityDetailsDialog_twelve_zero_Image',
                    'CapacityDetailsDialog_two_five_Capacity',
                    'CapacityDetailsDialog_two_five_Image',
                    'CapacityDetailsDialog_two_four_Capacity',
                    'CapacityDetailsDialog_two_four_Image',
                    'CapacityDetailsDialog_two_one_Capacity',
                    'CapacityDetailsDialog_two_one_Image',
                    'CapacityDetailsDialog_two_seven_Capacity',
                    'CapacityDetailsDialog_two_seven_Image',
                    'CapacityDetailsDialog_two_six_Capacity',
                    'CapacityDetailsDialog_two_six_Image',
                    'CapacityDetailsDialog_two_three_Capacity',
                    'CapacityDetailsDialog_two_three_Image',
                    'CapacityDetailsDialog_two_two_Capacity',
                    'CapacityDetailsDialog_two_two_Image',
                    'CapacityDetailsDialog_two_zero_Capacity',
                    'CapacityDetailsDialog_two_zero_Image',
                    'CapacityDetailsDialog_zero_five_Capacity',
                    'CapacityDetailsDialog_zero_five_Image',
                    'CapacityDetailsDialog_zero_four_Capacity',
                    'CapacityDetailsDialog_zero_four_Image',
                    'CapacityDetailsDialog_zero_one_Capacity',
                    'CapacityDetailsDialog_zero_one_Image',
                    'CapacityDetailsDialog_zero_seven_Capacity',
                    'CapacityDetailsDialog_zero_seven_Image',
                    'CapacityDetailsDialog_zero_six_Capacity',
                    'CapacityDetailsDialog_zero_six_Image',
                    'CapacityDetailsDialog_zero_three_Capacity',
                    'CapacityDetailsDialog_zero_three_Image',
                    'CapacityDetailsDialog_zero_two_Capacity',
                    'CapacityDetailsDialog_zero_two_Image',
                    'CapacityDetailsDialog_zero_zero_Capacity',
                    'CapacityDetailsDialog_zero_zero_Image',
                ]
            )
        except Exception as ex:
            logging.error(ex)
            sys.exit(1)

        # Get gui objects
        self.CapacityDetailsDialog = \
            self.builder.get_object('CapacityDetailsDialog')
        self.CapacityDetailsDialog_Close = \
            self.builder.get_object('CapacityDetailsDialog_Close')
        self.CapacityDetailsDialog_Msg = \
            self.builder.get_object('CapacityDetailsDialog_Msg')
        self.CapacityDetailsDialog_SourceCapacity = \
            self.builder.get_object('CapacityDetailsDialog_SourceCapacity')
        self.CapacityDetailsDialog_SourceImage = \
            self.builder.get_object('CapacityDetailsDialog_SourceImage')
        self.CapacityDetailsDialog_Title = \
            self.builder.get_object('CapacityDetailsDialog_Title')
        self.CapacityDetailsDialog_eight_five_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_eight_five_Capacity')
        self.CapacityDetailsDialog_eight_five_Image = \
            self.builder.get_object('CapacityDetailsDialog_eight_five_Image')
        self.CapacityDetailsDialog_eight_four_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_eight_four_Capacity')
        self.CapacityDetailsDialog_eight_four_Image = \
            self.builder.get_object('CapacityDetailsDialog_eight_four_Image')
        self.CapacityDetailsDialog_eight_one_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_eight_one_Capacity')
        self.CapacityDetailsDialog_eight_one_Image = \
            self.builder.get_object('CapacityDetailsDialog_eight_one_Image')
        self.CapacityDetailsDialog_eight_seven_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_eight_seven_Capacity')
        self.CapacityDetailsDialog_eight_seven_Image = \
            self.builder.get_object('CapacityDetailsDialog_eight_seven_Image')
        self.CapacityDetailsDialog_eight_six_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_eight_six_Capacity')
        self.CapacityDetailsDialog_eight_six_Image = \
            self.builder.get_object('CapacityDetailsDialog_eight_six_Image')
        self.CapacityDetailsDialog_eight_three_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_eight_three_Capacity')
        self.CapacityDetailsDialog_eight_three_Image = \
            self.builder.get_object('CapacityDetailsDialog_eight_three_Image')
        self.CapacityDetailsDialog_eight_two_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_eight_two_Capacity')
        self.CapacityDetailsDialog_eight_two_Image = \
            self.builder.get_object('CapacityDetailsDialog_eight_two_Image')
        self.CapacityDetailsDialog_eight_zero_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_eight_zero_Capacity')
        self.CapacityDetailsDialog_eight_zero_Image = \
            self.builder.get_object('CapacityDetailsDialog_eight_zero_Image')
        self.CapacityDetailsDialog_eleven_five_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_eleven_five_Capacity')
        self.CapacityDetailsDialog_eleven_five_Image = \
            self.builder.get_object('CapacityDetailsDialog_eleven_five_Image')
        self.CapacityDetailsDialog_eleven_four_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_eleven_four_Capacity')
        self.CapacityDetailsDialog_eleven_four_Image = \
            self.builder.get_object('CapacityDetailsDialog_eleven_four_Image')
        self.CapacityDetailsDialog_eleven_one_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_eleven_one_Capacity')
        self.CapacityDetailsDialog_eleven_one_Image = \
            self.builder.get_object('CapacityDetailsDialog_eleven_one_Image')
        self.CapacityDetailsDialog_eleven_seven_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_eleven_seven_Capacity')
        self.CapacityDetailsDialog_eleven_seven_Image = \
            self.builder.get_object('CapacityDetailsDialog_eleven_seven_Image')
        self.CapacityDetailsDialog_eleven_six_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_eleven_six_Capacity')
        self.CapacityDetailsDialog_eleven_six_Image = \
            self.builder.get_object('CapacityDetailsDialog_eleven_six_Image')
        self.CapacityDetailsDialog_eleven_three_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_eleven_three_Capacity')
        self.CapacityDetailsDialog_eleven_three_Image = \
            self.builder.get_object('CapacityDetailsDialog_eleven_three_Image')
        self.CapacityDetailsDialog_eleven_two_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_eleven_two_Capacity')
        self.CapacityDetailsDialog_eleven_two_Image = \
            self.builder.get_object('CapacityDetailsDialog_eleven_two_Image')
        self.CapacityDetailsDialog_eleven_zero_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_eleven_zero_Capacity')
        self.CapacityDetailsDialog_eleven_zero_Image = \
            self.builder.get_object('CapacityDetailsDialog_eleven_zero_Image')
        self.CapacityDetailsDialog_fifteen_five_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_fifteen_five_Capacity')
        self.CapacityDetailsDialog_fifteen_five_Image = \
            self.builder.get_object('CapacityDetailsDialog_fifteen_five_Image')
        self.CapacityDetailsDialog_fifteen_four_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_fifteen_four_Capacity')
        self.CapacityDetailsDialog_fifteen_four_Image = \
            self.builder.get_object('CapacityDetailsDialog_fifteen_four_Image')
        self.CapacityDetailsDialog_fifteen_one_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_fifteen_one_Capacity')
        self.CapacityDetailsDialog_fifteen_one_Image = \
            self.builder.get_object('CapacityDetailsDialog_fifteen_one_Image')
        self.CapacityDetailsDialog_fifteen_seven_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_fifteen_seven_Capacity')
        self.CapacityDetailsDialog_fifteen_seven_Image = \
            self.builder.get_object('CapacityDetailsDialog_fifteen_seven_Image')
        self.CapacityDetailsDialog_fifteen_six_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_fifteen_six_Capacity')
        self.CapacityDetailsDialog_fifteen_six_Image = \
            self.builder.get_object('CapacityDetailsDialog_fifteen_six_Image')
        self.CapacityDetailsDialog_fifteen_three_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_fifteen_three_Capacity')
        self.CapacityDetailsDialog_fifteen_three_Image = \
            self.builder.get_object('CapacityDetailsDialog_fifteen_three_Image')
        self.CapacityDetailsDialog_fifteen_two_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_fifteen_two_Capacity')
        self.CapacityDetailsDialog_fifteen_two_Image = \
            self.builder.get_object('CapacityDetailsDialog_fifteen_two_Image')
        self.CapacityDetailsDialog_fifteen_zero_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_fifteen_zero_Capacity')
        self.CapacityDetailsDialog_fifteen_zero_Image = \
            self.builder.get_object('CapacityDetailsDialog_fifteen_zero_Image')
        self.CapacityDetailsDialog_five_five_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_five_five_Capacity')
        self.CapacityDetailsDialog_five_five_Image = \
            self.builder.get_object('CapacityDetailsDialog_five_five_Image')
        self.CapacityDetailsDialog_five_four_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_five_four_Capacity')
        self.CapacityDetailsDialog_five_four_Image = \
            self.builder.get_object('CapacityDetailsDialog_five_four_Image')
        self.CapacityDetailsDialog_five_one_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_five_one_Capacity')
        self.CapacityDetailsDialog_five_one_Image = \
            self.builder.get_object('CapacityDetailsDialog_five_one_Image')
        self.CapacityDetailsDialog_five_seven_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_five_seven_Capacity')
        self.CapacityDetailsDialog_five_seven_Image = \
            self.builder.get_object('CapacityDetailsDialog_five_seven_Image')
        self.CapacityDetailsDialog_five_six_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_five_six_Capacity')
        self.CapacityDetailsDialog_five_six_Image = \
            self.builder.get_object('CapacityDetailsDialog_five_six_Image')
        self.CapacityDetailsDialog_five_three_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_five_three_Capacity')
        self.CapacityDetailsDialog_five_three_Image = \
            self.builder.get_object('CapacityDetailsDialog_five_three_Image')
        self.CapacityDetailsDialog_five_two_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_five_two_Capacity')
        self.CapacityDetailsDialog_five_two_Image = \
            self.builder.get_object('CapacityDetailsDialog_five_two_Image')
        self.CapacityDetailsDialog_five_zero_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_five_zero_Capacity')
        self.CapacityDetailsDialog_five_zero_Image = \
            self.builder.get_object('CapacityDetailsDialog_five_zero_Image')
        self.CapacityDetailsDialog_four_five_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_four_five_Capacity')
        self.CapacityDetailsDialog_four_five_Image = \
            self.builder.get_object('CapacityDetailsDialog_four_five_Image')
        self.CapacityDetailsDialog_four_four_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_four_four_Capacity')
        self.CapacityDetailsDialog_four_four_Image = \
            self.builder.get_object('CapacityDetailsDialog_four_four_Image')
        self.CapacityDetailsDialog_four_one_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_four_one_Capacity')
        self.CapacityDetailsDialog_four_one_Image = \
            self.builder.get_object('CapacityDetailsDialog_four_one_Image')
        self.CapacityDetailsDialog_four_seven_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_four_seven_Capacity')
        self.CapacityDetailsDialog_four_seven_Image = \
            self.builder.get_object('CapacityDetailsDialog_four_seven_Image')
        self.CapacityDetailsDialog_four_six_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_four_six_Capacity')
        self.CapacityDetailsDialog_four_six_Image = \
            self.builder.get_object('CapacityDetailsDialog_four_six_Image')
        self.CapacityDetailsDialog_four_three_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_four_three_Capacity')
        self.CapacityDetailsDialog_four_three_Image = \
            self.builder.get_object('CapacityDetailsDialog_four_three_Image')
        self.CapacityDetailsDialog_four_two_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_four_two_Capacity')
        self.CapacityDetailsDialog_four_two_Image = \
            self.builder.get_object('CapacityDetailsDialog_four_two_Image')
        self.CapacityDetailsDialog_four_zero_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_four_zero_Capacity')
        self.CapacityDetailsDialog_four_zero_Image = \
            self.builder.get_object('CapacityDetailsDialog_four_zero_Image')
        self.CapacityDetailsDialog_fourteen_five_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_fourteen_five_Capacity')
        self.CapacityDetailsDialog_fourteen_five_Image = \
            self.builder.get_object('CapacityDetailsDialog_fourteen_five_Image')
        self.CapacityDetailsDialog_fourteen_four_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_fourteen_four_Capacity')
        self.CapacityDetailsDialog_fourteen_four_Image = \
            self.builder.get_object('CapacityDetailsDialog_fourteen_four_Image')
        self.CapacityDetailsDialog_fourteen_one_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_fourteen_one_Capacity')
        self.CapacityDetailsDialog_fourteen_one_Image = \
            self.builder.get_object('CapacityDetailsDialog_fourteen_one_Image')
        self.CapacityDetailsDialog_fourteen_seven_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_fourteen_seven_Capacity')
        self.CapacityDetailsDialog_fourteen_seven_Image = \
            self.builder.get_object('CapacityDetailsDialog_fourteen_seven_Image')
        self.CapacityDetailsDialog_fourteen_six_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_fourteen_six_Capacity')
        self.CapacityDetailsDialog_fourteen_six_Image = \
            self.builder.get_object('CapacityDetailsDialog_fourteen_six_Image')
        self.CapacityDetailsDialog_fourteen_three_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_fourteen_three_Capacity')
        self.CapacityDetailsDialog_fourteen_three_Image = \
            self.builder.get_object('CapacityDetailsDialog_fourteen_three_Image')
        self.CapacityDetailsDialog_fourteen_two_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_fourteen_two_Capacity')
        self.CapacityDetailsDialog_fourteen_two_Image = \
            self.builder.get_object('CapacityDetailsDialog_fourteen_two_Image')
        self.CapacityDetailsDialog_fourteen_zero_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_fourteen_zero_Capacity')
        self.CapacityDetailsDialog_fourteen_zero_Image = \
            self.builder.get_object('CapacityDetailsDialog_fourteen_zero_Image')
        self.CapacityDetailsDialog_nine_five_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_nine_five_Capacity')
        self.CapacityDetailsDialog_nine_five_Image = \
            self.builder.get_object('CapacityDetailsDialog_nine_five_Image')
        self.CapacityDetailsDialog_nine_four_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_nine_four_Capacity')
        self.CapacityDetailsDialog_nine_four_Image = \
            self.builder.get_object('CapacityDetailsDialog_nine_four_Image')
        self.CapacityDetailsDialog_nine_one_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_nine_one_Capacity')
        self.CapacityDetailsDialog_nine_one_Image = \
            self.builder.get_object('CapacityDetailsDialog_nine_one_Image')
        self.CapacityDetailsDialog_nine_seven_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_nine_seven_Capacity')
        self.CapacityDetailsDialog_nine_seven_Image = \
            self.builder.get_object('CapacityDetailsDialog_nine_seven_Image')
        self.CapacityDetailsDialog_nine_six_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_nine_six_Capacity')
        self.CapacityDetailsDialog_nine_six_Image = \
            self.builder.get_object('CapacityDetailsDialog_nine_six_Image')
        self.CapacityDetailsDialog_nine_three_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_nine_three_Capacity')
        self.CapacityDetailsDialog_nine_three_Image = \
            self.builder.get_object('CapacityDetailsDialog_nine_three_Image')
        self.CapacityDetailsDialog_nine_two_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_nine_two_Capacity')
        self.CapacityDetailsDialog_nine_two_Image = \
            self.builder.get_object('CapacityDetailsDialog_nine_two_Image')
        self.CapacityDetailsDialog_nine_zero_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_nine_zero_Capacity')
        self.CapacityDetailsDialog_nine_zero_Image = \
            self.builder.get_object('CapacityDetailsDialog_nine_zero_Image')
        self.CapacityDetailsDialog_one_five_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_one_five_Capacity')
        self.CapacityDetailsDialog_one_five_Image = \
            self.builder.get_object('CapacityDetailsDialog_one_five_Image')
        self.CapacityDetailsDialog_one_four_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_one_four_Capacity')
        self.CapacityDetailsDialog_one_four_Image = \
            self.builder.get_object('CapacityDetailsDialog_one_four_Image')
        self.CapacityDetailsDialog_one_one_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_one_one_Capacity')
        self.CapacityDetailsDialog_one_one_Image = \
            self.builder.get_object('CapacityDetailsDialog_one_one_Image')
        self.CapacityDetailsDialog_one_seven_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_one_seven_Capacity')
        self.CapacityDetailsDialog_one_seven_Image = \
            self.builder.get_object('CapacityDetailsDialog_one_seven_Image')
        self.CapacityDetailsDialog_one_six_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_one_six_Capacity')
        self.CapacityDetailsDialog_one_six_Image = \
            self.builder.get_object('CapacityDetailsDialog_one_six_Image')
        self.CapacityDetailsDialog_one_three_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_one_three_Capacity')
        self.CapacityDetailsDialog_one_three_Image = \
            self.builder.get_object('CapacityDetailsDialog_one_three_Image')
        self.CapacityDetailsDialog_one_two_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_one_two_Capacity')
        self.CapacityDetailsDialog_one_two_Image = \
            self.builder.get_object('CapacityDetailsDialog_one_two_Image')
        self.CapacityDetailsDialog_one_zero_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_one_zero_Capacity')
        self.CapacityDetailsDialog_one_zero_Image = \
            self.builder.get_object('CapacityDetailsDialog_one_zero_Image')
        self.CapacityDetailsDialog_seven_five_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_seven_five_Capacity')
        self.CapacityDetailsDialog_seven_five_Image = \
            self.builder.get_object('CapacityDetailsDialog_seven_five_Image')
        self.CapacityDetailsDialog_seven_four_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_seven_four_Capacity')
        self.CapacityDetailsDialog_seven_four_Image = \
            self.builder.get_object('CapacityDetailsDialog_seven_four_Image')
        self.CapacityDetailsDialog_seven_one_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_seven_one_Capacity')
        self.CapacityDetailsDialog_seven_one_Image = \
            self.builder.get_object('CapacityDetailsDialog_seven_one_Image')
        self.CapacityDetailsDialog_seven_seven_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_seven_seven_Capacity')
        self.CapacityDetailsDialog_seven_seven_Image = \
            self.builder.get_object('CapacityDetailsDialog_seven_seven_Image')
        self.CapacityDetailsDialog_seven_six_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_seven_six_Capacity')
        self.CapacityDetailsDialog_seven_six_Image = \
            self.builder.get_object('CapacityDetailsDialog_seven_six_Image')
        self.CapacityDetailsDialog_seven_three_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_seven_three_Capacity')
        self.CapacityDetailsDialog_seven_three_Image = \
            self.builder.get_object('CapacityDetailsDialog_seven_three_Image')
        self.CapacityDetailsDialog_seven_two_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_seven_two_Capacity')
        self.CapacityDetailsDialog_seven_two_Image = \
            self.builder.get_object('CapacityDetailsDialog_seven_two_Image')
        self.CapacityDetailsDialog_seven_zero_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_seven_zero_Capacity')
        self.CapacityDetailsDialog_seven_zero_Image = \
            self.builder.get_object('CapacityDetailsDialog_seven_zero_Image')
        self.CapacityDetailsDialog_six_five_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_six_five_Capacity')
        self.CapacityDetailsDialog_six_five_Image = \
            self.builder.get_object('CapacityDetailsDialog_six_five_Image')
        self.CapacityDetailsDialog_six_four_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_six_four_Capacity')
        self.CapacityDetailsDialog_six_four_Image = \
            self.builder.get_object('CapacityDetailsDialog_six_four_Image')
        self.CapacityDetailsDialog_six_one_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_six_one_Capacity')
        self.CapacityDetailsDialog_six_one_Image = \
            self.builder.get_object('CapacityDetailsDialog_six_one_Image')
        self.CapacityDetailsDialog_six_seven_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_six_seven_Capacity')
        self.CapacityDetailsDialog_six_seven_Image = \
            self.builder.get_object('CapacityDetailsDialog_six_seven_Image')
        self.CapacityDetailsDialog_six_six_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_six_six_Capacity')
        self.CapacityDetailsDialog_six_six_Image = \
            self.builder.get_object('CapacityDetailsDialog_six_six_Image')
        self.CapacityDetailsDialog_six_three_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_six_three_Capacity')
        self.CapacityDetailsDialog_six_three_Image = \
            self.builder.get_object('CapacityDetailsDialog_six_three_Image')
        self.CapacityDetailsDialog_six_two_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_six_two_Capacity')
        self.CapacityDetailsDialog_six_two_Image = \
            self.builder.get_object('CapacityDetailsDialog_six_two_Image')
        self.CapacityDetailsDialog_six_zero_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_six_zero_Capacity')
        self.CapacityDetailsDialog_six_zero_Image = \
            self.builder.get_object('CapacityDetailsDialog_six_zero_Image')
        self.CapacityDetailsDialog_ten_five_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_ten_five_Capacity')
        self.CapacityDetailsDialog_ten_five_Image = \
            self.builder.get_object('CapacityDetailsDialog_ten_five_Image')
        self.CapacityDetailsDialog_ten_four_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_ten_four_Capacity')
        self.CapacityDetailsDialog_ten_four_Image = \
            self.builder.get_object('CapacityDetailsDialog_ten_four_Image')
        self.CapacityDetailsDialog_ten_one_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_ten_one_Capacity')
        self.CapacityDetailsDialog_ten_one_Image = \
            self.builder.get_object('CapacityDetailsDialog_ten_one_Image')
        self.CapacityDetailsDialog_ten_seven_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_ten_seven_Capacity')
        self.CapacityDetailsDialog_ten_seven_Image = \
            self.builder.get_object('CapacityDetailsDialog_ten_seven_Image')
        self.CapacityDetailsDialog_ten_six_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_ten_six_Capacity')
        self.CapacityDetailsDialog_ten_six_Image = \
            self.builder.get_object('CapacityDetailsDialog_ten_six_Image')
        self.CapacityDetailsDialog_ten_three_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_ten_three_Capacity')
        self.CapacityDetailsDialog_ten_three_Image = \
            self.builder.get_object('CapacityDetailsDialog_ten_three_Image')
        self.CapacityDetailsDialog_ten_two_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_ten_two_Capacity')
        self.CapacityDetailsDialog_ten_two_Image = \
            self.builder.get_object('CapacityDetailsDialog_ten_two_Image')
        self.CapacityDetailsDialog_ten_zero_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_ten_zero_Capacity')
        self.CapacityDetailsDialog_ten_zero_Image = \
            self.builder.get_object('CapacityDetailsDialog_ten_zero_Image')
        self.CapacityDetailsDialog_thirteen_five_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_thirteen_five_Capacity')
        self.CapacityDetailsDialog_thirteen_five_Image = \
            self.builder.get_object('CapacityDetailsDialog_thirteen_five_Image')
        self.CapacityDetailsDialog_thirteen_four_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_thirteen_four_Capacity')
        self.CapacityDetailsDialog_thirteen_four_Image = \
            self.builder.get_object('CapacityDetailsDialog_thirteen_four_Image')
        self.CapacityDetailsDialog_thirteen_one_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_thirteen_one_Capacity')
        self.CapacityDetailsDialog_thirteen_one_Image = \
            self.builder.get_object('CapacityDetailsDialog_thirteen_one_Image')
        self.CapacityDetailsDialog_thirteen_seven_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_thirteen_seven_Capacity')
        self.CapacityDetailsDialog_thirteen_seven_Image = \
            self.builder.get_object('CapacityDetailsDialog_thirteen_seven_Image')
        self.CapacityDetailsDialog_thirteen_six_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_thirteen_six_Capacity')
        self.CapacityDetailsDialog_thirteen_six_Image = \
            self.builder.get_object('CapacityDetailsDialog_thirteen_six_Image')
        self.CapacityDetailsDialog_thirteen_three_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_thirteen_three_Capacity')
        self.CapacityDetailsDialog_thirteen_three_Image = \
            self.builder.get_object('CapacityDetailsDialog_thirteen_three_Image')
        self.CapacityDetailsDialog_thirteen_two_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_thirteen_two_Capacity')
        self.CapacityDetailsDialog_thirteen_two_Image = \
            self.builder.get_object('CapacityDetailsDialog_thirteen_two_Image')
        self.CapacityDetailsDialog_thirteen_zero_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_thirteen_zero_Capacity')
        self.CapacityDetailsDialog_thirteen_zero_Image = \
            self.builder.get_object('CapacityDetailsDialog_thirteen_zero_Image')
        self.CapacityDetailsDialog_three_five_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_three_five_Capacity')
        self.CapacityDetailsDialog_three_five_Image = \
            self.builder.get_object('CapacityDetailsDialog_three_five_Image')
        self.CapacityDetailsDialog_three_four_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_three_four_Capacity')
        self.CapacityDetailsDialog_three_four_Image = \
            self.builder.get_object('CapacityDetailsDialog_three_four_Image')
        self.CapacityDetailsDialog_three_one_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_three_one_Capacity')
        self.CapacityDetailsDialog_three_one_Image = \
            self.builder.get_object('CapacityDetailsDialog_three_one_Image')
        self.CapacityDetailsDialog_three_seven_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_three_seven_Capacity')
        self.CapacityDetailsDialog_three_seven_Image = \
            self.builder.get_object('CapacityDetailsDialog_three_seven_Image')
        self.CapacityDetailsDialog_three_six_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_three_six_Capacity')
        self.CapacityDetailsDialog_three_six_Image = \
            self.builder.get_object('CapacityDetailsDialog_three_six_Image')
        self.CapacityDetailsDialog_three_three_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_three_three_Capacity')
        self.CapacityDetailsDialog_three_three_Image = \
            self.builder.get_object('CapacityDetailsDialog_three_three_Image')
        self.CapacityDetailsDialog_three_two_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_three_two_Capacity')
        self.CapacityDetailsDialog_three_two_Image = \
            self.builder.get_object('CapacityDetailsDialog_three_two_Image')
        self.CapacityDetailsDialog_three_zero_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_three_zero_Capacity')
        self.CapacityDetailsDialog_three_zero_Image = \
            self.builder.get_object('CapacityDetailsDialog_three_zero_Image')
        self.CapacityDetailsDialog_twelve_five_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_twelve_five_Capacity')
        self.CapacityDetailsDialog_twelve_five_Image = \
            self.builder.get_object('CapacityDetailsDialog_twelve_five_Image')
        self.CapacityDetailsDialog_twelve_four_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_twelve_four_Capacity')
        self.CapacityDetailsDialog_twelve_four_Image = \
            self.builder.get_object('CapacityDetailsDialog_twelve_four_Image')
        self.CapacityDetailsDialog_twelve_one_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_twelve_one_Capacity')
        self.CapacityDetailsDialog_twelve_one_Image = \
            self.builder.get_object('CapacityDetailsDialog_twelve_one_Image')
        self.CapacityDetailsDialog_twelve_seven_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_twelve_seven_Capacity')
        self.CapacityDetailsDialog_twelve_seven_Image = \
            self.builder.get_object('CapacityDetailsDialog_twelve_seven_Image')
        self.CapacityDetailsDialog_twelve_six_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_twelve_six_Capacity')
        self.CapacityDetailsDialog_twelve_six_Image = \
            self.builder.get_object('CapacityDetailsDialog_twelve_six_Image')
        self.CapacityDetailsDialog_twelve_three_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_twelve_three_Capacity')
        self.CapacityDetailsDialog_twelve_three_Image = \
            self.builder.get_object('CapacityDetailsDialog_twelve_three_Image')
        self.CapacityDetailsDialog_twelve_two_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_twelve_two_Capacity')
        self.CapacityDetailsDialog_twelve_two_Image = \
            self.builder.get_object('CapacityDetailsDialog_twelve_two_Image')
        self.CapacityDetailsDialog_twelve_zero_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_twelve_zero_Capacity')
        self.CapacityDetailsDialog_twelve_zero_Image = \
            self.builder.get_object('CapacityDetailsDialog_twelve_zero_Image')
        self.CapacityDetailsDialog_two_five_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_two_five_Capacity')
        self.CapacityDetailsDialog_two_five_Image = \
            self.builder.get_object('CapacityDetailsDialog_two_five_Image')
        self.CapacityDetailsDialog_two_four_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_two_four_Capacity')
        self.CapacityDetailsDialog_two_four_Image = \
            self.builder.get_object('CapacityDetailsDialog_two_four_Image')
        self.CapacityDetailsDialog_two_one_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_two_one_Capacity')
        self.CapacityDetailsDialog_two_one_Image = \
            self.builder.get_object('CapacityDetailsDialog_two_one_Image')
        self.CapacityDetailsDialog_two_seven_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_two_seven_Capacity')
        self.CapacityDetailsDialog_two_seven_Image = \
            self.builder.get_object('CapacityDetailsDialog_two_seven_Image')
        self.CapacityDetailsDialog_two_six_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_two_six_Capacity')
        self.CapacityDetailsDialog_two_six_Image = \
            self.builder.get_object('CapacityDetailsDialog_two_six_Image')
        self.CapacityDetailsDialog_two_three_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_two_three_Capacity')
        self.CapacityDetailsDialog_two_three_Image = \
            self.builder.get_object('CapacityDetailsDialog_two_three_Image')
        self.CapacityDetailsDialog_two_two_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_two_two_Capacity')
        self.CapacityDetailsDialog_two_two_Image = \
            self.builder.get_object('CapacityDetailsDialog_two_two_Image')
        self.CapacityDetailsDialog_two_zero_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_two_zero_Capacity')
        self.CapacityDetailsDialog_two_zero_Image = \
            self.builder.get_object('CapacityDetailsDialog_two_zero_Image')
        self.CapacityDetailsDialog_zero_five_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_zero_five_Capacity')
        self.CapacityDetailsDialog_zero_five_Image = \
            self.builder.get_object('CapacityDetailsDialog_zero_five_Image')
        self.CapacityDetailsDialog_zero_four_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_zero_four_Capacity')
        self.CapacityDetailsDialog_zero_four_Image = \
            self.builder.get_object('CapacityDetailsDialog_zero_four_Image')
        self.CapacityDetailsDialog_zero_one_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_zero_one_Capacity')
        self.CapacityDetailsDialog_zero_one_Image = \
            self.builder.get_object('CapacityDetailsDialog_zero_one_Image')
        self.CapacityDetailsDialog_zero_seven_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_zero_seven_Capacity')
        self.CapacityDetailsDialog_zero_seven_Image = \
            self.builder.get_object('CapacityDetailsDialog_zero_seven_Image')
        self.CapacityDetailsDialog_zero_six_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_zero_six_Capacity')
        self.CapacityDetailsDialog_zero_six_Image = \
            self.builder.get_object('CapacityDetailsDialog_zero_six_Image')
        self.CapacityDetailsDialog_zero_three_Capacity =\
            self.builder.get_object('CapacityDetailsDialog_zero_three_Capacity')
        self.CapacityDetailsDialog_zero_three_Image = \
            self.builder.get_object('CapacityDetailsDialog_zero_three_Image')
        self.CapacityDetailsDialog_zero_two_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_zero_two_Capacity')
        self.CapacityDetailsDialog_zero_two_Image = \
            self.builder.get_object('CapacityDetailsDialog_zero_two_Image')
        self.CapacityDetailsDialog_zero_zero_Capacity = \
            self.builder.get_object('CapacityDetailsDialog_zero_zero_Capacity')
        self.CapacityDetailsDialog_zero_zero_Image = \
            self.builder.get_object('CapacityDetailsDialog_zero_zero_Image')
        self.CapacityDetailsDialog.show_all()
        self.builder.connect_signals(self)

        self.source_by_path = EZDuplicator.lib.EZDuplicator.get_config_setting('source_dev_path')
        self.targets = EZDuplicator.lib.EZDuplicator.get_number_or_list_of_usbs('list', self.source_by_path)

        if EZDuplicator.lib.EZDuplicator.is_source_connected(
                EZDuplicator.lib.EZDuplicator.get_config_setting('source_dev_path')):
            self.source_bytes = EZDuplicator.lib.EZDuplicator.get_size_in_bytes(self.source_by_path)
            self.source_size = EZDuplicator.lib.DataOnlyDuplication.get_human_size(self.source_bytes, decimal_place=3)
            self.CapacityDetailsDialog_SourceCapacity.set_text(self.source_size)

        for target in self.targets:
            xy = EZDuplicator.lib.QA.get_x_and_y(EZDuplicator.lib.QA.get_disk_by_path(target))
            bites = EZDuplicator.lib.EZDuplicator.get_size_in_bytes(target)
            size = EZDuplicator.lib.DataOnlyDuplication.get_human_size(bites, decimal_place=3)
            
            if xy == "00":
                """ self.zero_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_zero_zero_Capacity.set_text(size)
            elif xy == "01":
                """ self.zero_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_zero_one_Capacity.set_text(size)
            elif xy == "02":
                """ self.zero_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_zero_two_Capacity.set_text(size)
            elif xy == "03":
                """ self.zero_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_zero_three_Capacity.set_text(size)
            elif xy == "04":
                """ self.zero_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_zero_four_Capacity.set_text(size)
            elif xy == "05":
                """ self.zero_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_zero_five_Capacity.set_text(size)
            elif xy == "06":
                """ self.zero_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_zero_six_Capacity.set_text(size)
            elif xy == "07":
                """ self.zero_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_zero_seven_Capacity.set_text(size)
            elif xy == "10":
                """ self.one_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_one_zero_Capacity.set_text(size)
            elif xy == "11":
                """ self.one_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_one_one_Capacity.set_text(size)
            elif xy == "12":
                """ self.one_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_one_two_Capacity.set_text(size)
            elif xy == "13":
                """ self.one_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_one_three_Capacity.set_text(size)
            elif xy == "14":
                """ self.one_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_one_four_Capacity.set_text(size)
            elif xy == "15":
                """ self.one_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_one_five_Capacity.set_text(size)
            elif xy == "16":
                """ self.one_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_one_six_Capacity.set_text(size)
            elif xy == "17":
                """ self.one_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_one_seven_Capacity.set_text(size)
            elif xy == "20":
                """ self.two_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_two_zero_Capacity.set_text(size)
            elif xy == "21":
                """ self.two_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_two_one_Capacity.set_text(size)
            elif xy == "22":
                """ self.two_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_two_two_Capacity.set_text(size)
            elif xy == "23":
                """ self.two_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_two_three_Capacity.set_text(size)
            elif xy == "24":
                """ self.two_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_two_four_Capacity.set_text(size)
            elif xy == "25":
                """ self.two_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_two_five_Capacity.set_text(size)
            elif xy == "26":
                """ self.two_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_two_six_Capacity.set_text(size)
            elif xy == "27":
                """ self.two_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_two_seven_Capacity.set_text(size)
            elif xy == "30":
                """ self.three_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_three_zero_Capacity.set_text(size)
            elif xy == "31":
                """ self.three_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_three_one_Capacity.set_text(size)
            elif xy == "32":
                """ self.three_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_three_two_Capacity.set_text(size)
            elif xy == "33":
                """ self.three_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_three_three_Capacity.set_text(size)
            elif xy == "34":
                """ self.three_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_three_four_Capacity.set_text(size)
            elif xy == "35":
                """ self.three_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_three_five_Capacity.set_text(size)
            elif xy == "36":
                """ self.three_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_three_six_Capacity.set_text(size)
            elif xy == "37":
                """ self.three_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_three_seven_Capacity.set_text(size)
            elif xy == "40":
                """ self.four_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_four_zero_Capacity.set_text(size)
            elif xy == "41":
                """ self.four_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_four_one_Capacity.set_text(size)
            elif xy == "42":
                """ self.four_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_four_two_Capacity.set_text(size)
            elif xy == "43":
                """ self.four_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_four_three_Capacity.set_text(size)
            elif xy == "44":
                """ self.four_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_four_four_Capacity.set_text(size)
            elif xy == "45":
                """ self.four_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_four_five_Capacity.set_text(size)
            elif xy == "46":
                """ self.four_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_four_six_Capacity.set_text(size)
            elif xy == "47":
                """ self.four_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_four_seven_Capacity.set_text(size)
            elif xy == "50":
                """ self.five_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_five_zero_Capacity.set_text(size)
            elif xy == "51":
                """ self.five_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_five_one_Capacity.set_text(size)
            elif xy == "52":
                """ self.five_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_five_two_Capacity.set_text(size)
            elif xy == "53":
                """ self.five_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_five_three_Capacity.set_text(size)
            elif xy == "54":
                """ self.five_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_five_four_Capacity.set_text(size)
            elif xy == "55":
                """ self.five_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_five_five_Capacity.set_text(size)
            elif xy == "56":
                """ self.five_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_five_six_Capacity.set_text(size)
            elif xy == "57":
                """ self.five_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_five_seven_Capacity.set_text(size)
            elif xy == "60":
                """ self.six_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_six_zero_Capacity.set_text(size)
            elif xy == "61":
                """ self.six_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_six_one_Capacity.set_text(size)
            elif xy == "62":
                """ self.six_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_six_two_Capacity.set_text(size)
            elif xy == "63":
                """ self.six_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_six_three_Capacity.set_text(size)
            elif xy == "64":
                """ self.six_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_six_four_Capacity.set_text(size)
            elif xy == "65":
                """ self.six_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_six_five_Capacity.set_text(size)
            elif xy == "66":
                """ self.six_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_six_six_Capacity.set_text(size)
            elif xy == "67":
                """ self.six_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_six_seven_Capacity.set_text(size)
            elif xy == "70":
                """ self.seven_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_seven_zero_Capacity.set_text(size)
            elif xy == "71":
                """ self.seven_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_seven_one_Capacity.set_text(size)
            elif xy == "72":
                """ self.seven_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_seven_two_Capacity.set_text(size)
            elif xy == "73":
                """ self.seven_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_seven_three_Capacity.set_text(size)
            elif xy == "74":
                """ self.seven_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_seven_four_Capacity.set_text(size)
            elif xy == "75":
                """ self.seven_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_seven_five_Capacity.set_text(size)
            elif xy == "76":
                """ self.seven_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_seven_six_Capacity.set_text(size)
            elif xy == "77":
                """ self.seven_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_seven_seven_Capacity.set_text(size)
            elif xy == "80":
                """ self.eight_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_eight_zero_Capacity.set_text(size)
            elif xy == "81":
                """ self.eight_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_eight_one_Capacity.set_text(size)
            elif xy == "82":
                """ self.eight_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_eight_two_Capacity.set_text(size)
            elif xy == "83":
                """ self.eight_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_eight_three_Capacity.set_text(size)
            elif xy == "84":
                """ self.eight_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_eight_four_Capacity.set_text(size)
            elif xy == "85":
                """ self.eight_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_eight_five_Capacity.set_text(size)
            elif xy == "86":
                """ self.eight_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_eight_six_Capacity.set_text(size)
            elif xy == "87":
                """ self.eight_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_eight_seven_Capacity.set_text(size)
            elif xy == "90":
                """ self.nine_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_nine_zero_Capacity.set_text(size)
            elif xy == "91":
                """ self.nine_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_nine_one_Capacity.set_text(size)
            elif xy == "92":
                """ self.nine_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_nine_two_Capacity.set_text(size)
            elif xy == "93":
                """ self.nine_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_nine_three_Capacity.set_text(size)
            elif xy == "94":
                """ self.nine_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_nine_four_Capacity.set_text(size)
            elif xy == "95":
                """ self.nine_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_nine_five_Capacity.set_text(size)
            elif xy == "96":
                """ self.nine_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_nine_six_Capacity.set_text(size)
            elif xy == "97":
                """ self.nine_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_nine_seven_Capacity.set_text(size)
            elif xy == "100":
                """ self.ten_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_ten_zero_Capacity.set_text(size)
            elif xy == "101":
                """ self.ten_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_ten_one_Capacity.set_text(size)
            elif xy == "102":
                """ self.ten_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_ten_two_Capacity.set_text(size)
            elif xy == "103":
                """ self.ten_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_ten_three_Capacity.set_text(size)
            elif xy == "104":
                """ self.ten_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_ten_four_Capacity.set_text(size)
            elif xy == "105":
                """ self.ten_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_ten_five_Capacity.set_text(size)
            elif xy == "106":
                """ self.ten_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_ten_six_Capacity.set_text(size)
            elif xy == "107":
                """ self.ten_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_ten_seven_Capacity.set_text(size)
            elif xy == "110":
                """ self.eleven_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_eleven_zero_Capacity.set_text(size)
            elif xy == "111":
                """ self.eleven_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_eleven_one_Capacity.set_text(size)
            elif xy == "112":
                """ self.eleven_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_eleven_two_Capacity.set_text(size)
            elif xy == "113":
                """ self.eleven_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_eleven_three_Capacity.set_text(size)
            elif xy == "114":
                """ self.eleven_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_eleven_four_Capacity.set_text(size)
            elif xy == "115":
                """ self.eleven_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_eleven_five_Capacity.set_text(size)
            elif xy == "116":
                """ self.eleven_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_eleven_six_Capacity.set_text(size)
            elif xy == "117":
                """ self.eleven_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_eleven_seven_Capacity.set_text(size)
            elif xy == "120":
                """ self.twelve_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_twelve_zero_Capacity.set_text(size)
            elif xy == "121":
                """ self.twelve_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_twelve_one_Capacity.set_text(size)
            elif xy == "122":
                """ self.twelve_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_twelve_two_Capacity.set_text(size)
            elif xy == "123":
                """ self.twelve_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_twelve_three_Capacity.set_text(size)
            elif xy == "124":
                """ self.twelve_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_twelve_four_Capacity.set_text(size)
            elif xy == "125":
                """ self.twelve_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_twelve_five_Capacity.set_text(size)
            elif xy == "126":
                """ self.twelve_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_twelve_six_Capacity.set_text(size)
            elif xy == "127":
                """ self.twelve_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_twelve_seven_Capacity.set_text(size)
            elif xy == "130":
                """ self.thirteen_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_thirteen_zero_Capacity.set_text(size)
            elif xy == "131":
                """ self.thirteen_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_thirteen_one_Capacity.set_text(size)
            elif xy == "132":
                """ self.thirteen_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_thirteen_two_Capacity.set_text(size)
            elif xy == "133":
                """ self.thirteen_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_thirteen_three_Capacity.set_text(size)
            elif xy == "134":
                """ self.thirteen_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_thirteen_four_Capacity.set_text(size)
            elif xy == "135":
                """ self.thirteen_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_thirteen_five_Capacity.set_text(size)
            elif xy == "136":
                """ self.thirteen_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_thirteen_six_Capacity.set_text(size)
            elif xy == "137":
                """ self.thirteen_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_thirteen_seven_Capacity.set_text(size)
            elif xy == "140":
                """ self.fourteen_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_fourteen_zero_Capacity.set_text(size)
            elif xy == "141":
                """ self.fourteen_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_fourteen_one_Capacity.set_text(size)
            elif xy == "142":
                """ self.fourteen_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_fourteen_two_Capacity.set_text(size)
            elif xy == "143":
                """ self.fourteen_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_fourteen_three_Capacity.set_text(size)
            elif xy == "144":
                """ self.fourteen_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_fourteen_four_Capacity.set_text(size)
            elif xy == "145":
                """ self.fourteen_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_fourteen_five_Capacity.set_text(size)
            elif xy == "146":
                """ self.fourteen_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_fourteen_six_Capacity.set_text(size)
            elif xy == "147":
                """ self.fourteen_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_fourteen_seven_Capacity.set_text(size)
            elif xy == "150":
                """ self.fifteen_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_fifteen_zero_Capacity.set_text(size)
            elif xy == "151":
                """ self.fifteen_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_fifteen_one_Capacity.set_text(size)
            elif xy == "152":
                """ self.fifteen_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_fifteen_two_Capacity.set_text(size)
            elif xy == "153":
                """ self.fifteen_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_fifteen_three_Capacity.set_text(size)
            elif xy == "154":
                """ self.fifteen_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_fifteen_four_Capacity.set_text(size)
            elif xy == "155":
                """ self.fifteen_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_fifteen_five_Capacity.set_text(size)
            elif xy == "156":
                """ self.fifteen_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_fifteen_six_Capacity.set_text(size)
            elif xy == "157":
                """ self.fifteen_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png") """
                self.CapacityDetailsDialog_fifteen_seven_Capacity.set_text(size)
                
    def on_CapacityDetailsDialog_Close_clicked(self, widget, user_data=None):
        """ Handler for CapacityDetailsDialog_Close.clicked. """
        self.CapacityDetailsDialog.destroy()

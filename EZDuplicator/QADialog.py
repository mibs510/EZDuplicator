"""

Copyright (c) 2021 Connor McMillan <connor@mcmillan.website>. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

"""
import logging
import os
import sys
from pathlib import Path

from gi import require_version as gi_require_version

import EZDuplicator.lib.QA

gi_require_version('Gtk', '3.0')

from gi.repository import Gtk


class QADialog(Gtk.Dialog):
    """ Main window with all components. """

    def __init__(self, title, msg, *abs_blkdevs):
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
                    'QADialog',
                    'QADialog_Close',
                    'QADialog_Msg',
                    'QADialog_Title',
                    'eight_five',
                    'eight_four',
                    'eight_one',
                    'eight_seven',
                    'eight_six',
                    'eight_three',
                    'eight_two',
                    'eight_zero',
                    'eleven_five',
                    'eleven_four',
                    'eleven_one',
                    'eleven_seven',
                    'eleven_six',
                    'eleven_three',
                    'eleven_two',
                    'eleven_zero',
                    'fifteen_five',
                    'fifteen_four',
                    'fifteen_one',
                    'fifteen_seven',
                    'fifteen_six',
                    'fifteen_three',
                    'fifteen_two',
                    'fifteen_zero',
                    'five_five',
                    'five_four',
                    'five_one',
                    'five_seven',
                    'five_six',
                    'five_three',
                    'five_two',
                    'five_zero',
                    'four_five',
                    'four_four',
                    'four_one',
                    'four_seven',
                    'four_six',
                    'four_three',
                    'four_two',
                    'four_zero',
                    'fourteen_five',
                    'fourteen_four',
                    'fourteen_one',
                    'fourteen_seven',
                    'fourteen_six',
                    'fourteen_three',
                    'fourteen_two',
                    'fourteen_zero',
                    'nine_five',
                    'nine_four',
                    'nine_one',
                    'nine_seven',
                    'nine_six',
                    'nine_three',
                    'nine_two',
                    'nine_zero',
                    'one_five',
                    'one_four',
                    'one_one',
                    'one_seven',
                    'one_six',
                    'one_three',
                    'one_two',
                    'one_zero',
                    'seven_five',
                    'seven_four',
                    'seven_one',
                    'seven_seven',
                    'seven_six',
                    'seven_three',
                    'seven_two',
                    'seven_zero',
                    'six_five',
                    'six_four',
                    'six_one',
                    'six_seven',
                    'six_six',
                    'six_three',
                    'six_two',
                    'six_zero',
                    'ten_five',
                    'ten_four',
                    'ten_one',
                    'ten_seven',
                    'ten_six',
                    'ten_three',
                    'ten_two',
                    'ten_zero',
                    'thirteen_five',
                    'thirteen_four',
                    'thirteen_one',
                    'thirteen_seven',
                    'thirteen_six',
                    'thirteen_three',
                    'thirteen_two',
                    'thirteen_zero',
                    'three_five',
                    'three_four',
                    'three_one',
                    'three_seven',
                    'three_six',
                    'three_three',
                    'three_two',
                    'three_zero',
                    'twelve_five',
                    'twelve_four',
                    'twelve_one',
                    'twelve_seven',
                    'twelve_six',
                    'twelve_three',
                    'twelve_two',
                    'twelve_zero',
                    'two_five',
                    'two_four',
                    'two_one',
                    'two_seven',
                    'two_six',
                    'two_three',
                    'two_two',
                    'two_zero',
                    'zero_five',
                    'zero_four',
                    'zero_one',
                    'zero_seven',
                    'zero_six',
                    'zero_three',
                    'zero_two',
                    'zero_zero',
                ]
            )
        except Exception as ex:
            logging.error(ex)

        # Get gui objects
        self.QADialog = self.builder.get_object('QADialog')
        self.QADialog_Close = self.builder.get_object('QADialog_Close')
        self.QADialog_Msg = self.builder.get_object('QADialog_Msg')
        self.QADialog_Title = self.builder.get_object('QADialog_Title')
        self.eight_five = self.builder.get_object('eight_five')
        self.eight_four = self.builder.get_object('eight_four')
        self.eight_one = self.builder.get_object('eight_one')
        self.eight_seven = self.builder.get_object('eight_seven')
        self.eight_six = self.builder.get_object('eight_six')
        self.eight_three = self.builder.get_object('eight_three')
        self.eight_two = self.builder.get_object('eight_two')
        self.eight_zero = self.builder.get_object('eight_zero')
        self.eleven_five = self.builder.get_object('eleven_five')
        self.eleven_four = self.builder.get_object('eleven_four')
        self.eleven_one = self.builder.get_object('eleven_one')
        self.eleven_seven = self.builder.get_object('eleven_seven')
        self.eleven_six = self.builder.get_object('eleven_six')
        self.eleven_three = self.builder.get_object('eleven_three')
        self.eleven_two = self.builder.get_object('eleven_two')
        self.eleven_zero = self.builder.get_object('eleven_zero')
        self.fifteen_five = self.builder.get_object('fifteen_five')
        self.fifteen_four = self.builder.get_object('fifteen_four')
        self.fifteen_one = self.builder.get_object('fifteen_one')
        self.fifteen_seven = self.builder.get_object('fifteen_seven')
        self.fifteen_six = self.builder.get_object('fifteen_six')
        self.fifteen_three = self.builder.get_object('fifteen_three')
        self.fifteen_two = self.builder.get_object('fifteen_two')
        self.fifteen_zero = self.builder.get_object('fifteen_zero')
        self.five_five = self.builder.get_object('five_five')
        self.five_four = self.builder.get_object('five_four')
        self.five_one = self.builder.get_object('five_one')
        self.five_seven = self.builder.get_object('five_seven')
        self.five_six = self.builder.get_object('five_six')
        self.five_three = self.builder.get_object('five_three')
        self.five_two = self.builder.get_object('five_two')
        self.five_zero = self.builder.get_object('five_zero')
        self.four_five = self.builder.get_object('four_five')
        self.four_four = self.builder.get_object('four_four')
        self.four_one = self.builder.get_object('four_one')
        self.four_seven = self.builder.get_object('four_seven')
        self.four_six = self.builder.get_object('four_six')
        self.four_three = self.builder.get_object('four_three')
        self.four_two = self.builder.get_object('four_two')
        self.four_zero = self.builder.get_object('four_zero')
        self.fourteen_five = self.builder.get_object('fourteen_five')
        self.fourteen_four = self.builder.get_object('fourteen_four')
        self.fourteen_one = self.builder.get_object('fourteen_one')
        self.fourteen_seven = self.builder.get_object('fourteen_seven')
        self.fourteen_six = self.builder.get_object('fourteen_six')
        self.fourteen_three = self.builder.get_object('fourteen_three')
        self.fourteen_two = self.builder.get_object('fourteen_two')
        self.fourteen_zero = self.builder.get_object('fourteen_zero')
        self.nine_five = self.builder.get_object('nine_five')
        self.nine_four = self.builder.get_object('nine_four')
        self.nine_one = self.builder.get_object('nine_one')
        self.nine_seven = self.builder.get_object('nine_seven')
        self.nine_six = self.builder.get_object('nine_six')
        self.nine_three = self.builder.get_object('nine_three')
        self.nine_two = self.builder.get_object('nine_two')
        self.nine_zero = self.builder.get_object('nine_zero')
        self.one_five = self.builder.get_object('one_five')
        self.one_four = self.builder.get_object('one_four')
        self.one_one = self.builder.get_object('one_one')
        self.one_seven = self.builder.get_object('one_seven')
        self.one_six = self.builder.get_object('one_six')
        self.one_three = self.builder.get_object('one_three')
        self.one_two = self.builder.get_object('one_two')
        self.one_zero = self.builder.get_object('one_zero')
        self.seven_five = self.builder.get_object('seven_five')
        self.seven_four = self.builder.get_object('seven_four')
        self.seven_one = self.builder.get_object('seven_one')
        self.seven_seven = self.builder.get_object('seven_seven')
        self.seven_six = self.builder.get_object('seven_six')
        self.seven_three = self.builder.get_object('seven_three')
        self.seven_two = self.builder.get_object('seven_two')
        self.seven_zero = self.builder.get_object('seven_zero')
        self.six_five = self.builder.get_object('six_five')
        self.six_four = self.builder.get_object('six_four')
        self.six_one = self.builder.get_object('six_one')
        self.six_seven = self.builder.get_object('six_seven')
        self.six_six = self.builder.get_object('six_six')
        self.six_three = self.builder.get_object('six_three')
        self.six_two = self.builder.get_object('six_two')
        self.six_zero = self.builder.get_object('six_zero')
        self.ten_five = self.builder.get_object('ten_five')
        self.ten_four = self.builder.get_object('ten_four')
        self.ten_one = self.builder.get_object('ten_one')
        self.ten_seven = self.builder.get_object('ten_seven')
        self.ten_six = self.builder.get_object('ten_six')
        self.ten_three = self.builder.get_object('ten_three')
        self.ten_two = self.builder.get_object('ten_two')
        self.ten_zero = self.builder.get_object('ten_zero')
        self.thirteen_five = self.builder.get_object('thirteen_five')
        self.thirteen_four = self.builder.get_object('thirteen_four')
        self.thirteen_one = self.builder.get_object('thirteen_one')
        self.thirteen_seven = self.builder.get_object('thirteen_seven')
        self.thirteen_six = self.builder.get_object('thirteen_six')
        self.thirteen_three = self.builder.get_object('thirteen_three')
        self.thirteen_two = self.builder.get_object('thirteen_two')
        self.thirteen_zero = self.builder.get_object('thirteen_zero')
        self.three_five = self.builder.get_object('three_five')
        self.three_four = self.builder.get_object('three_four')
        self.three_one = self.builder.get_object('three_one')
        self.three_seven = self.builder.get_object('three_seven')
        self.three_six = self.builder.get_object('three_six')
        self.three_three = self.builder.get_object('three_three')
        self.three_two = self.builder.get_object('three_two')
        self.three_zero = self.builder.get_object('three_zero')
        self.twelve_five = self.builder.get_object('twelve_five')
        self.twelve_four = self.builder.get_object('twelve_four')
        self.twelve_one = self.builder.get_object('twelve_one')
        self.twelve_seven = self.builder.get_object('twelve_seven')
        self.twelve_six = self.builder.get_object('twelve_six')
        self.twelve_three = self.builder.get_object('twelve_three')
        self.twelve_two = self.builder.get_object('twelve_two')
        self.twelve_zero = self.builder.get_object('twelve_zero')
        self.two_five = self.builder.get_object('two_five')
        self.two_four = self.builder.get_object('two_four')
        self.two_one = self.builder.get_object('two_one')
        self.two_seven = self.builder.get_object('two_seven')
        self.two_six = self.builder.get_object('two_six')
        self.two_three = self.builder.get_object('two_three')
        self.two_two = self.builder.get_object('two_two')
        self.two_zero = self.builder.get_object('two_zero')
        self.zero_five = self.builder.get_object('zero_five')
        self.zero_four = self.builder.get_object('zero_four')
        self.zero_one = self.builder.get_object('zero_one')
        self.zero_seven = self.builder.get_object('zero_seven')
        self.zero_six = self.builder.get_object('zero_six')
        self.zero_three = self.builder.get_object('zero_three')
        self.zero_two = self.builder.get_object('zero_two')
        self.zero_zero = self.builder.get_object('zero_zero')
        self.QADialog.show_all()
        self.builder.connect_signals(self)
        self.QADialog_Title.set_text(title)
        self.QADialog_Msg.set_text(msg)

        for abs_blkdev in abs_blkdevs[0]:
            xy = EZDuplicator.lib.QA.get_x_and_y(EZDuplicator.lib.QA.get_disk_by_path(abs_blkdev))
            if xy == "00":
                self.zero_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "01":
                self.zero_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "02":
                self.zero_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "03":
                self.zero_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "04":
                self.zero_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "05":
                self.zero_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "06":
                self.zero_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "07":
                self.zero_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "10":
                self.one_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "11":
                self.one_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "12":
                self.one_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "13":
                self.one_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "14":
                self.one_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "15":
                self.one_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "16":
                self.one_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "17":
                self.one_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "20":
                self.two_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "21":
                self.two_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "22":
                self.two_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "23":
                self.two_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "24":
                self.two_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "25":
                self.two_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "26":
                self.two_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "27":
                self.two_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "30":
                self.three_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "31":
                self.three_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "32":
                self.three_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "33":
                self.three_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "34":
                self.three_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "35":
                self.three_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "36":
                self.three_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "37":
                self.three_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "40":
                self.four_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "41":
                self.four_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "42":
                self.four_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "43":
                self.four_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "44":
                self.four_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "45":
                self.four_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "46":
                self.four_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "47":
                self.four_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "50":
                self.five_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "51":
                self.five_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "52":
                self.five_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "53":
                self.five_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "54":
                self.five_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "55":
                self.five_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "56":
                self.five_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "57":
                self.five_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "60":
                self.six_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "61":
                self.six_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "62":
                self.six_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "63":
                self.six_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "64":
                self.six_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "65":
                self.six_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "66":
                self.six_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "67":
                self.six_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "70":
                self.seven_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "71":
                self.seven_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "72":
                self.seven_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "73":
                self.seven_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "74":
                self.seven_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "75":
                self.seven_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "76":
                self.seven_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "77":
                self.seven_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "80":
                self.eight_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "81":
                self.eight_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "82":
                self.eight_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "83":
                self.eight_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "84":
                self.eight_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "85":
                self.eight_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "86":
                self.eight_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "87":
                self.eight_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "90":
                self.nine_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "91":
                self.nine_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "92":
                self.nine_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "93":
                self.nine_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "94":
                self.nine_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "95":
                self.nine_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "96":
                self.nine_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "97":
                self.nine_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "100":
                self.ten_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "101":
                self.ten_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "102":
                self.ten_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "103":
                self.ten_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "104":
                self.ten_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "105":
                self.ten_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "106":
                self.ten_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "107":
                self.ten_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "110":
                self.eleven_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "111":
                self.eleven_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "112":
                self.eleven_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "113":
                self.eleven_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "114":
                self.eleven_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "115":
                self.eleven_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "116":
                self.eleven_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "117":
                self.eleven_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "120":
                self.twelve_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "121":
                self.twelve_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "122":
                self.twelve_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "123":
                self.twelve_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "124":
                self.twelve_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "125":
                self.twelve_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "126":
                self.twelve_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "127":
                self.twelve_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "130":
                self.thirteen_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "131":
                self.thirteen_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "132":
                self.thirteen_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "133":
                self.thirteen_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "134":
                self.thirteen_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "135":
                self.thirteen_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "136":
                self.thirteen_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "137":
                self.thirteen_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "140":
                self.fourteen_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "141":
                self.fourteen_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "142":
                self.fourteen_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "143":
                self.fourteen_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "144":
                self.fourteen_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "145":
                self.fourteen_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "146":
                self.fourteen_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "147":
                self.fourteen_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "150":
                self.fifteen_zero.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "151":
                self.fifteen_one.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "152":
                self.fifteen_two.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "153":
                self.fifteen_three.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "154":
                self.fifteen_four.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "155":
                self.fifteen_five.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "156":
                self.fifteen_six.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")
            elif xy == "157":
                self.fifteen_seven.set_from_file(str(Path(__file__).parent.absolute()) + "/res/red-usb-port-32.png")

    def on_QADialog_Close_clicked(self, widget, user_data=None):
        """ Handler for QADialog_Close.clicked. """
        self.QADialog.destroy()

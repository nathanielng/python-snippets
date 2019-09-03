#!/usr/bin/env python

import argparse
import datetime
import dateutil
import humanize


class Subscription:


    def __init__(self, start_day, qty, unit):
        self._start_day = start_day
        self._now = datetime.datetime.now()
        self._start_date = self.get_start_date(self._now, start_day)
        self._t_elapsed, self._t_frac = self.get_elapsed_frac()
        self._qty = qty
        self._unit = unit


    def get_start_date(self, now, start_day):
        """
        Gets the start date of a monthly subscription
        plan that starts on `start_day`
        """
        yr = self._now.year
        if self._now.day < 11:
            if self._now.month == 1:
                mth = 12
                yr = self._now.year - 1
            else:
                mth = self._now.month - 1
        else:
            mth = self._now.month
        return datetime.datetime(
            year=yr, month=mth, day=start_day)


    def get_elapsed_frac(self):
        """
        Get the time elpased and the elapsed fraction
        since the start of a monthly subscription
        """
        t_elapsed = self._now - self._start_date
        t_frac = t_elapsed.days + t_elapsed.seconds/86400
        return t_elapsed, t_frac


    def print_subscription_status(self):
        txt_now = self._now.strftime('%Y%m%d %H%Mh')
        txt_start = self._start_date.strftime('%Y%m%d %H%Mh')
        t_frac_30 = self._t_frac / 30
        t_percent = 100.0 * t_frac_30
        max_usage = self._qty * t_percent / 100.0

        print(f'Subscription start: {txt_start}')
        print(f'Now (today)       : {txt_now}')
        print()
        print(f'Time elapsed      : {str(self._t_elapsed)}')
        print(f'Fraction          : {t_percent:.2f}% ({t_frac_30:.2f} days / 30 days)')
        print(f'Usage should be < {self._qty} {self._unit}' +
            f' x {t_percent:.2f}% = {max_usage:.2f} {self._unit}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--start')
    parser.add_argument('--qty')
    parser.add_argument('--unit')
    args = parser.parse_args()

    plan = Subscription(
        start_day=int(args.start),
        qty=float(args.qty),
        unit=args.unit)
    plan.print_subscription_status()

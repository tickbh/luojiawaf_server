import re
class AccessUrl:
    def __init__(self, urlraw):
        matchObj = re.match( r'(.*):_:(.*):(.*)', urlraw, re.M|re.I)
        if matchObj:
            self.url = matchObj.group(1)
            self.access = float(matchObj.group(2))
            self.cost = float(matchObj.group(3))
        else:
            self.url = "/"
            self.access = 0
            self.cost = 0
    
    def __str__(self):
        return "url:%s, access:%f cost:%f" % (self.url, self.access, self.cost)

def calc_not_wait_count(all_visit_table):
    not_wait_count = 0
    all_count = 0
    for (k, v) in all_visit_table.items():
        all_count += len(v)
        v.sort(key=lambda elem: elem.access)
        all_cost_time = 0
        for t in v:
            all_cost_time += t.cost

        ingore_cost = all_cost_time * 3 / len(v)
        next_request_time = 0
        for t in v:
            if t.cost > ingore_cost:
                continue
            if not next_request_time:
                next_request_time = t.access + t.cost
            else:
                if t.access < next_request_time:
                    not_wait_count += 1
                next_request_time = max(t.access + t.cost, next_request_time)
    
    return not_wait_count, all_count

def test_accessUrl():
    access = AccessUrl("/sys/login_config:_:1635736494.566:0.37800")
    assert access.url == "/sys/login_config"
    assert access.access == 1635736494.566
    assert access.cost == 0.37800
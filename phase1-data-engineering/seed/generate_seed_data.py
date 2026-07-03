import csv
import os
import random
from datetime import timedelta
from faker import Faker

BASE_DIR = os.path.dirname(__file__)
OUTPUT_DIR = BASE_DIR
os.makedirs(OUTPUT_DIR, exist_ok=True)

fake = Faker()

products = [
    ("PIVC-001", "Peripheral IV Catheter", "DEV-PIVC", "2019-03-15"),
    ("SYR-001", "Safety Syringe", "DEV-SYR", "2020-01-10"),
    ("IVS-001", "IV Infusion Set", "DEV-IVS", "2018-11-05"),
    ("NGT-001", "Nasogastric Tube", "DEV-NGT", "2021-07-20"),
    ("FOL-001", "Foley Catheter", "DEV-FOL", "2019-09-18"),
    ("CVC-001", "Central Venous Catheter", "DEV-CVC", "2020-05-22"),
    ("BAG-001", "Urine Collection Bag", "DEV-BAG", "2018-08-30"),
    ("EXT-001", "Extension Set", "DEV-EXT", "2021-02-15"),
    ("CAN-001", "IV Cannula", "DEV-CAN", "2022-04-01"),
    ("TUB-001", "Feeding Tube", "DEV-TUB", "2019-12-12"),
]

imdrf_codes = [
    ("A0101","A","Mechanical failure"),
    ("A0102","A","Leakage detected"),
    ("A0103","A","Needle breakage"),
    ("A0104","A","Occlusion"),
    ("E0201","E","Minor injury"),
    ("E0202","E","Major injury"),
    ("E0203","E","Patient discomfort"),
    ("F0301","F","Packaging defect"),
    ("F0302","F","Labeling error"),
    ("F0303","F","Sterility issue"),
]

def write_csv(filename, headers, rows):
    with open(os.path.join(OUTPUT_DIR, filename),"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)
    print(f"Created {filename}")

write_csv("products.csv",
["product_code","product_name","device_code","launch_date"],products)

write_csv("imdrf_codes.csv",
["imdrf_code","code_level","description"],imdrf_codes)

statuses=["Open","Investigating","Closed","Reopened"]
markets=["US","EU","UK","Canada","Japan","APAC"]

complaints=[]
for i in range(1,51):
    cid=f"CMP-{i:06d}"
    p=random.choice(products)[0]
    ic=random.choice(imdrf_codes)[0]
    rd=fake.date_between(start_date="-2y", end_date="today")
    if random.random()<0.3:
        cd=None
        status=random.choice(["Open","Investigating"])
    else:
        cd=rd+timedelta(days=random.randint(1,30))
        status=random.choice(["Closed","Reopened"])
    complaints.append((
        cid,p,rd,cd,fake.sentence(nb_words=10),ic,random.choice(markets),status
    ))

write_csv("complaints.csv",
["complaint_id","product_code","received_date","close_date","event_description","imdrf_code","regulatory_market","status"],
complaints)

investigations=[]
for idx,c in enumerate(random.sample(complaints,35),1):
    start=c[2]
    close=start+timedelta(days=random.randint(1,20))
    investigations.append((
        f"INV-{idx:06d}",c[0],start,close,
        random.choice(["Manufacturing","User Error","Material Defect","Unknown"]),
        fake.name(),
        fake.sentence(nb_words=12)
    ))

write_csv("investigations.csv",
["investigation_id","complaint_id","investigation_start_date","investigation_close_date","root_cause_category","investigator","findings"],
investigations)

mdr=[]
for idx,c in enumerate(random.sample(complaints,30),1):
    mdr.append((
        f"MDR-{idx:06d}",
        c[0],
        random.choice([True,False]),
        c[2]+timedelta(days=random.randint(1,15)),
        fake.name(),
        fake.sentence(nb_words=14)
    ))

write_csv("mdr_decisions.csv",
["mdr_decision_id","complaint_id","is_reportable","decision_date","decided_by","rationale"],
mdr)

events=[]
eid=1
for c in complaints:
    cid,status=c[0],c[7]
    events.append((f"EVT-{eid:06d}",cid,None,"Open",c[2],fake.name()))
    eid+=1
    if status in ("Investigating","Closed","Reopened"):
        events.append((f"EVT-{eid:06d}",cid,"Open","Investigating",c[2]+timedelta(days=2),fake.name()))
        eid+=1
    if status=="Closed":
        events.append((f"EVT-{eid:06d}",cid,"Investigating","Closed",c[2]+timedelta(days=10),fake.name()))
        eid+=1
    if status=="Reopened":
        events.append((f"EVT-{eid:06d}",cid,"Investigating","Closed",c[2]+timedelta(days=10),fake.name()))
        eid+=1
        events.append((f"EVT-{eid:06d}",cid,"Closed","Reopened",c[2]+timedelta(days=20),fake.name()))
        eid+=1

write_csv("complaint_events.csv",
["event_id","complaint_id","old_status","new_status","event_date","changed_by"],
events)

print("Seed generation completed.")

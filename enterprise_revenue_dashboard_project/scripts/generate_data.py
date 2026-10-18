"""Generates a synthetic enterprise dataset for the Power BI revenue dashboard.
Pure standard library. Run: python generate_data.py  (writes CSVs to ../data)
Seeded, so results are reproducible."""
import csv, random, os
from datetime import date, timedelta
random.seed(42)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

regions = [
 (1,"North America","United States","Americas"),(2,"North America","Canada","Americas"),
 (3,"Latin America","Brazil","Americas"),(4,"Europe","Germany","EMEA"),
 (5,"Europe","United Kingdom","EMEA"),(6,"Europe","France","EMEA"),
 (7,"Middle East & Africa","UAE","EMEA"),(8,"Asia Pacific","India","APAC"),
 (9,"Asia Pacific","Japan","APAC"),(10,"Asia Pacific","Australia","APAC")]
channels = [(1,"Direct Sales","Offline"),(2,"Online Store","Online"),
            (3,"Distributors","Partner"),(4,"Retail Partners","Partner"),(5,"Marketplace","Online")]
products = []
cats = {"Laptops":(1200,.72),"Monitors":(350,.68),"Networking":(220,.60),
        "Software Licences":(500,.25),"Accessories":(60,.55),"Support Services":(300,.35)}
pid = 1
for c,(p,cr) in cats.items():
    for k in range(1,6):
        price = round(p*random.uniform(.7,1.4),2)
        products.append((pid,f"{c} Item {k}",c,price,round(cr*random.uniform(.9,1.1),3))); pid+=1

segments = ["Enterprise","Mid-Market","SMB"]
customers = []
first = ["Apex","Nova","Zenith","Orion","Vertex","Helix","Quanta","Summit","Pioneer","Atlas",
         "Cobalt","Ember","Lumen","Titan","Aurora","Crest","Delta","Echo","Fusion","Gravity"]
last = ["Systems","Logistics","Retail","Health","Finance","Energy","Media","Foods","Motors","Labs"]
used=set()
for cid in range(1,401):
    n=f"{random.choice(first)} {random.choice(last)}"
    if n in used: n=f"{n} {random.choice(['Group','Corp','Ltd','Inc','GmbH','Holdings'])}"
    while n in used: n=f"{n} {cid}"
    used.add(n)
    seg=random.choices(segments,[.2,.35,.45])[0]
    reg=random.choice(regions)[0]
    signup=date(2021,1,1)+timedelta(days=random.randint(0,1000))
    discounter = random.random()<.12          # heavy discounters -> low-margin accounts
    churn_after = None
    if random.random()<.15:                   # churners stop buying
        churn_after = date(2025,6,1)+timedelta(days=random.randint(-300,250))
    customers.append(dict(id=cid,name=n,seg=seg,reg=reg,signup=signup,disc=discounter,churn=churn_after))

def w(name, header, rows):
    with open(os.path.join(OUT,name),"w",newline="",encoding="utf-8") as f:
        wr=csv.writer(f); wr.writerow(header); wr.writerows(rows)

w("dim_region.csv",["RegionID","Region","Country","Territory"],regions)
w("dim_channel.csv",["ChannelID","Channel","ChannelType"],channels)
w("dim_product.csv",["ProductID","ProductName","Category","ListPrice","CostRatio"],products)
w("dim_customer.csv",["CustomerID","CustomerName","Segment","RegionID","SignupDate"],
  [(c["id"],c["name"],c["seg"],c["reg"],c["signup"].isoformat()) for c in customers])

start,end = date(2023,1,1), date(2026,9,30)
days=(end-start).days
seg_w={"Enterprise":3.0,"Mid-Market":1.5,"SMB":.6}
chan_disc={1:.08,2:.03,3:.14,4:.10,5:.05}
sales=[]; oid=100000
for c in customers:
    n_orders = max(int(random.gauss(55,18)*seg_w[c["seg"]]/1.5)+5,3)
    for _ in range(n_orders):
        d = start+timedelta(days=random.randint(0,days))
        if d<c["signup"]: d=c["signup"]+timedelta(days=random.randint(0,60))
        if d>end: continue
        if c["churn"] and d>c["churn"]: continue
        if d.year==2023 and random.random()<.18: continue   # mild growth over time
        ch=random.choices([x[0] for x in channels],[.3,.25,.2,.15,.1])[0]
        p=random.choice(products)
        qty=random.randint(1,12 if c["seg"]!="SMB" else 5)
        disc=min(.45,max(0,random.gauss(chan_disc[ch],.03)+(.16 if c["disc"] else 0)))
        price=round(p[3]*random.uniform(.97,1.03)*(1+0.03*(d.year-2023)),2)
        net=round(qty*price*(1-disc),2)
        cogs=round(qty*p[3]*p[4]*(1+0.02*(d.year-2023)),2)
        oid+=1
        sales.append((oid,d.isoformat(),c["id"],p[0],ch,c["reg"],qty,price,round(disc,4),net,cogs))
sales.sort(key=lambda r:r[1])
w("fact_sales.csv",["OrderID","OrderDate","CustomerID","ProductID","ChannelID","RegionID",
  "Quantity","UnitPrice","DiscountPct","NetRevenue","COGS"],sales)

agg={}
for r in sales:
    k=(r[1][:7],r[5],r[4]); agg[k]=agg.get(k,0)+r[9]
targets=[]
y,mo=2023,1
while date(y,mo,1)<=end:
    ym=f"{y}-{mo:02d}"
    for rg in regions:
        for ch in channels:
            base=agg.get((ym,rg[0],ch[0]),0) or 3000
            targets.append((f"{ym}-01",rg[0],ch[0],round(base*random.uniform(.88,1.18),2)))
    mo+=1
    if mo==13: y+=1; mo=1
w("fact_target.csv",["TargetMonth","RegionID","ChannelID","RevenueTarget"],targets)
print("rows:",len(sales),"sales,",len(targets),"targets,",len(customers),"customers")

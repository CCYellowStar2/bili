from flask import Flask, request, redirect
import json
import requests
import time
import xml.etree.ElementTree as ET
import numpy as np
import random

headers = {
    "cookie": "buvid4=9D715CF5-4326-1CB0-134C-10363A1F230344345-022060710-3RZtRYV5AZewWHGrlokJoQ%3D%3D; buvid3=FD39475C-DA34-2D57-CACA-CD2D5A064B4956972infoc; b_nut=1702722756; i-wanna-go-back=-1; b_ut=7; _uuid=FF212E33-4DA7-FECE-72C3-EF10102529471745090infoc; enable_web_push=DISABLE; header_theme_version=CLOSE; buvid_fp_plain=undefined; CURRENT_FNVAL=16; rpdid=|(~J|~Ylm)m0J'u~|k~JJY~Y; is-2022-channel=1; PVID=2; DedeUserID=350809631; DedeUserID__ckMd5=5c596f5bf64d5d39; SESSDATA=e006fa46%2C1741696973%2Cb6c8b%2A91CjAaHy9D_DaBh63XgJyFOdWr01M5hd1KYffO2TGS20-0q60GoJF7ht2lVN6nCDxcX_kSVjBDOThMTk8yWUdyNHpyVkY4WjdLTG9hU1pJanp5azZ1ZENzUEtVcmhYUjQ4ZTJwVTk0STR5ellCZENRQ25oRmMza0pFVEJLWjJ4MUNFenQ4b0Q0V2ZnIIEC; bili_jct=a72da1b3186e988000edc6a03f55f3d6; sid=5cklih49; b_lsid=F6CABDE6_191F0C67B88; bmg_af_switch=1; bmg_src_def_domain=i2.hdslb.com; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjY1ODA3MjcsImlhdCI6MTcyNjMyMTQ2NywicGx0IjotMX0.6N75Zbxfp1haEP6Ip6miQh3fRsVni0mSo5aYkShG5aU; bili_ticket_expires=1726580667; fingerprint=538a5048bbd52a0d08f978717fa0bb45; buvid_fp=538a5048bbd52a0d08f978717fa0bb45; bp_t_offset_350809631=977032650986356736; browser_resolution=751-949; home_feed_column=4",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35",
}
    
app = Flask(__name__)

@app.route('/play')
def play():
    complete_url = request.args.get('url')

    if complete_url:
        # 分割字符串并获取BV号，它通常位于"/video/"之后
        parts = complete_url.split('/video/')
        bv_part = parts[1] if len(parts) > 1 else None
        bv = bv_part.split('?')[0] if bv_part else None
        bv = bv.rstrip('/') if bv else None
        # 获取p参数，查找'?p='或'&p='后面的值，如果不存在则默认为'1'
        p = '1'  # 默认值为'1'
        for delimiter in ['?p=', '&p=']:
            delimiter_index = complete_url.find(delimiter)
            if delimiter_index != -1:
                p_start = delimiter_index + len(delimiter)
                p_end = complete_url.find('&', p_start)
                if p_end == -1:  # 如果没找到其他参数，获取p到末尾的部分
                    p = complete_url[p_start:]
                else:
                    p = complete_url[p_start:p_end]
                p = p.strip()  # 去除可能出现的空格
                break 
    print(bv+p)            
    url = 'https://api.bilibili.com/x/web-interface/view/detail'
    params = {'bvid': bv}
    max_retries = 10
    retry_count = 0
    cid=""
    while retry_count < max_retries:
        if not cid:
            response = requests.get(url, params=params, headers=headers)
        
        if cid or response.status_code == 200:
            if not cid:
                json_data = response.json()
                cid = json_data["data"]["View"]["pages"][int(p)-1]["cid"]
                print(cid)
            qn_values = [80, 0]        
            for qn in qn_values:
                url2 = f"https://api.bilibili.com/x/player/playurl?cid={cid}&bvid={bv}&platform=html5&high_quality=1&qn={qn}"
                response2 = requests.get(url2, headers=headers)
                if response2.status_code == 200:
                    json_data2 = response2.json()
                    video_url = json_data2["data"]["durl"][0]["url"]
                    if qn==0:
                        print(str(qn)+" " +str(json_data2["data"]["durl"][0]["size"]))
                        return redirect(video_url)
                    try:
                        with requests.get(video_url, stream=True, timeout=3) as res:
                            print(str(qn)+" " +str(res.status_code)+" " +str(json_data2["data"]["durl"][0]["size"]))
                            content_type = res.headers.get('Content-Type', '')
                            if 'text/html' in content_type:
                                print("g")
                                continue
                            return redirect(video_url)
                    except:
                        if qn==0:
                            return redirect(video_url)
#           qn_values = [80, 64, 32, 16, 0]        
#            for qn in qn_values:
#               url2 = f"https://api.bilibili.com/x/player/playurl?cid={cid}&bvid={bv}&platform=html5&high_quality=1&qn={qn}"
#                response2 = requests.get(url2, headers=headers)
#                if response2.status_code == 200:
#                    json_data2 = response2.json()
#                    video_url = json_data2["data"]["durl"][0]["url"]
#                    with requests.get(video_url, stream=True) as res:
#                        print(str(qn)+" " +str(res.status_code)+" " +str(json_data2["data"]["durl"][0]["size"]))
#                        if res.status_code != 403:
#                            # 如果状态码不是403，返回视频URL
#                            return redirect(video_url)
#                        else:
#                            if qn==0:
#                                return redirect(video_url)
            else:
                print(f"Failed to fetch data. Status code: {response2.status_code}. Retrying...")
                retry_count += 1
                time.sleep(1)  
            break
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}. Retrying...")
            retry_count += 1
            time.sleep(1)  
    if retry_count == max_retries:
        return f"Failed to fetch data. Status code: {response.status_code}"
                

@app.route('/')
def home():
    bv = request.args.get('bv')
    p = request.args.get('p', default= 1, type=int)
    url = 'https://api.bilibili.com/x/web-interface/view/detail'
    params = {'bvid': bv}
    max_retries = 10
    retry_count = 0
    cid=""
    title=""
    owner=""
    page=[]
    
    while retry_count < max_retries:
        if not cid:
            response = requests.get(url, params=params, headers=headers)
        
        if cid or response.status_code == 200:
            if not cid:
                json_data = response.json()
                title= json_data["data"]["View"]["title"]
                owner= json_data["data"]["View"]["owner"]["name"]
                cid = json_data["data"]["View"]["pages"][int(p)-1]["cid"]
                page = json_data["data"]["View"]["pages"]
                print(cid)
            url2= f"https://comment.bilibili.com/{cid}.xml"
            response2 = requests.get(url2, headers=headers)
            if response2.status_code == 200:
                root = ET.fromstring(response2.content)
                # 为每个条目创建一个特征元组，包括p和文本值
                entries = [(d.attrib['p'], d.text) for d in root.findall('d')]
            
                # 提取每个条目的第一个和第二个逗号前的数字
                p_values = np.array([entry[0] for entry in entries])
                first_comma_values = np.array([float(p.split(',')[0]) for p in p_values])
                second_comma_values = np.array([float(p.split(',')[1]) for p in p_values])
            
                # 对于相同的第一个逗号前的数字，按照第二个逗号前的数字排序
                sorted_indices = np.lexsort((second_comma_values, first_comma_values))
            
                # 输出排序后的结果
                sorted_entries = np.array(entries)[sorted_indices]
                comments_list = [{"info": comment[0], "text": comment[1].replace("[", "（").replace("]", "）").replace("［", "（").replace("］", "）")} for comment in sorted_entries]
                result = {
                    "code": 200,
                    "title": title,
                    "owner": owner,
                    "bv": bv,
                    "p": str(p),
                    "data": comments_list,
                    "pages": page
                }
                json_data2 = json.dumps(result, ensure_ascii=False)
                return json_data2
            else:
                print(f"Failed to fetch data. Status code: {response2.status_code}. Retrying...")
                retry_count += 1
                time.sleep(1)  
            break
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}. Retrying...")
            retry_count += 1
            time.sleep(1)  
    if retry_count == max_retries:
        return f"Failed to fetch data. Status code: {response.status_code}"

@app.route('/live')
def live():
    id = request.args.get('id')
    url = f'https://api.live.bilibili.com/room/v1/Room/get_info?room_id={id}'
    response = requests.get(url, headers=headers)
    json_data = response.json()
    uid = json_data["data"]["uid"]
    url2 = f"https://api.live.bilibili.com/live_user/v1/Master/info?uid={uid}"
    response2 = requests.get(url2, headers=headers)
    json_data2 = response2.json()
    uname = json_data2["data"]["info"]["uname"]
        # 在原始JSON中插入新的键值对
    json_data["data"]["uname"] = uname

    return json_data

@app.route('/search')
def search():
    keyword = request.args.get('keyword')
    page = request.args.get('page', default= "1")
    url = f'https://api.bilibili.com/x/web-interface/wbi/search/all/v2?keyword={keyword}&page={page}'
    response = requests.get(url, headers=headers)
    json_data = response.json()
    return json_data

@app.route('/live/search')
def livesearch():
    keyword = request.args.get('keyword')
    page = request.args.get('page', default= "1")
    url = f'https://api.bilibili.com/x/web-interface/wbi/search/type?search_type=live_room&keyword={keyword}&page={page}'
    response = requests.get(url, headers=headers)
    json_data = response.json()
    return json_data

@app.route('/index')
def index():
    page = request.args.get('page', default= "1")
    url = f'https://api.bilibili.com/x/web-interface/index/top/rcmd?ps=14&version=1'
    response = requests.get(url, headers=headers)
    json_data = response.json()
    return json_data

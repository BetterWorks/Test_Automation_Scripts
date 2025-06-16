import requests
import pandas as pd
from deep_translator import GoogleTranslator
from sentence_transformers import SentenceTransformer, util
import languages
import test

# API endpoint and headers
# feedback_api_url = "https://data-platform.teams.betterworks.com/accelerators/llm/assistant/feedback"
# feedback_api_url = "http://localhost:9090/accelerators/llm/assistant/feedback"
rainforest_api_url = "https://rainforest.betterworks.com/accelerators/llm/assistant/feedback"

# Load the sentence transformer model for semantic similarity
model = SentenceTransformer('all-MiniLM-L6-v2')

# Supported languages by Llama 3.2 (example list)
supported_languages = languages.llama_languages_sanity_tests

# Function to send feedback to the assistant API
def get_rephrased_feedback(feedback):

    payload = {
        "content": feedback,
        "details": True,
        # "context": "1. Provide some feedback about this person.",
        "context": "3. Para 3",
        "word_limit": None,
        # "session_id": "2952ea73-3a28-4f25-8409-5fc3c004253a",
        "session_id": "e746aaec-9a08-47be-9868-e5c0b19af442",
        "iterations": []
    }
    # headers = {
        
    #     'X-CSRFToken': 'PM9XkCSknL3bc63Uo8T21QseCjN2oYyNKs1GAQLI9IMguShf3HrL8jNVx9zBhjds',
    #     'Authorization': "Token 33a9e3d8-42d5-4f13-8a51-2730d45171f5",
    #     'Cookie': 'mp_108cea758e4afadad33545771a85c8ce_mixpanel=%7B%22distinct_id%22%3A%20%22aakansha.srivastava%40betterworks.com%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%7D; first_visit_url=https://www.betterworks.com/; _mkto_trk=id:133-YCN-039&token:_mch-betterworks.com-1706552720607-92718; _biz_uid=1124676ba79f45d395c6599952f8d5a5; _ga_FD90Y8GQGR=GS1.2.1706552720.1.0.1706552720.60.0.0; _biz_flagsA=%7B%22Version%22%3A1%2C%22Mkto%22%3A%221%22%2C%22ViewThrough%22%3A%221%22%2C%22XDomain%22%3A%221%22%7D; _ce.irv=new; cebs=1; _vwo_uuid_v2=D900203F43D8E74B465515F1E8EDE5736|aca63d702358ce08f14bda79a2ba9c0d; mp_dddd49acc22c844b6f90427030f38120_mixpanel=%7B%22distinct_id%22%3A%20%22664329%22%2C%22%24device_id%22%3A%20%221905a1c9dff17cb-027e61cb4b412a-19525637-1d73c0-1905a1c9e0017cb%22%2C%22mp_lib%22%3A%20%22Segment%3A%20web%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%2C%22__mps%22%3A%20%7B%7D%2C%22__mpso%22%3A%20%7B%7D%2C%22__mpus%22%3A%20%7B%7D%2C%22__mpa%22%3A%20%7B%7D%2C%22__mpu%22%3A%20%7B%7D%2C%22__mpr%22%3A%20%5B%5D%2C%22__mpap%22%3A%20%5B%5D%2C%22%24user_id%22%3A%20%22664329%22%2C%22mp_name_tag%22%3A%20%22aakansha.srivastava%40betterworks.com%22%2C%22user_uuid%22%3A%20%2284e0593c-c29c-4a2e-b0d2-5a33e1099463%22%2C%22goalmaster%22%3A%20false%2C%22admin_group_uuids%22%3A%20%5B%0A%20%20%20%20%221242c72b-43f7-49dd-9716-5bad95c09edb%22%2C%0A%20%20%20%20%229a690fc3-3a67-4d62-a46a-cd8902dd19d9%22%0A%5D%2C%22manager_id%22%3A%20null%2C%22is_manager%22%3A%20false%2C%22org%22%3A%20%22BetterWorks%22%2C%22org_id%22%3A%201%2C%22org_uuid%22%3A%20%22403a44af-7d45-45e7-b460-ae5a912d76bb%22%2C%22timezone%22%3A%20%22Asia%2FKolkata%22%2C%22is_super_admin%22%3A%20false%2C%22is_admin%22%3A%20false%2C%22is_group_admin%22%3A%20false%2C%22groupId%22%3A%201%2C%22locale%22%3A%20%22en%22%2C%22id%22%3A%20%22664329%22%2C%22%24created%22%3A%20%222023-03-16T17%3A52%3A00.000Z%22%2C%22%24email%22%3A%20%22aakansha.srivastava%40betterworks.com%22%2C%22came_from%22%3A%20%22%2F%22%7D; _ga_KGTSTVSJX4=GS1.2.1719498744.1.1.1719498744.0.0.0; mp_1275c5d092aaec694b419c77e1cce879_mixpanel=%7B%22distinct_id%22%3A%20%22142855%22%2C%22%24device_id%22%3A%20%221905a1a824d1653-06d8df6558b974-19525637-1d73c0-1905a1a824d1654%22%2C%22mp_lib%22%3A%20%22Segment%3A%20web%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%2C%22__mps%22%3A%20%7B%7D%2C%22__mpso%22%3A%20%7B%7D%2C%22__mpus%22%3A%20%7B%7D%2C%22__mpa%22%3A%20%7B%7D%2C%22__mpu%22%3A%20%7B%7D%2C%22__mpr%22%3A%20%5B%5D%2C%22__mpap%22%3A%20%5B%5D%2C%22%24user_id%22%3A%20%22142855%22%2C%22mp_name_tag%22%3A%20%22aakansha.srivastava%40betterworks.com%22%2C%22user_uuid%22%3A%20%226e8e092b-f699-4602-bd13-91139dc98b6d%22%2C%22goalmaster%22%3A%20false%2C%22admin_group_uuids%22%3A%20%5B%5D%2C%22manager_id%22%3A%20null%2C%22is_manager%22%3A%20false%2C%22org%22%3A%20%22BetterWorks%22%2C%22org_id%22%3A%201%2C%22org_uuid%22%3A%20%228825b49a-a02b-4f8b-96da-2feb65bd3f96%22%2C%22timezone%22%3A%20%22Asia%2FKolkata%22%2C%22is_super_admin%22%3A%20false%2C%22is_admin%22%3A%20false%2C%22is_group_admin%22%3A%20false%2C%22groupId%22%3A%20%228825b49a-a02b-4f8b-96da-2feb65bd3f96%22%2C%22locale%22%3A%20%22en_GB%22%2C%22id%22%3A%20%22142855%22%2C%22%24created%22%3A%20%222023-07-25T11%3A18%3A12.000Z%22%2C%22%24email%22%3A%20%22aakansha.srivastava%40betterworks.com%22%2C%22came_from%22%3A%20%22%2F%22%7D; mp_dbaf4eb08ba45118434f514f698c36e7_mixpanel=%7B%22distinct_id%22%3A%20%221314%22%2C%22%24device_id%22%3A%20%2218a27ad575713f4-039b5add6d3a71-1a525634-1d73c0-18a27ad575713f4%22%2C%22mp_lib%22%3A%20%22Segment%3A%20web%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%2C%22%24user_id%22%3A%20%221314%22%2C%22mp_name_tag%22%3A%20%22aakansha.srivastava%40betterworks.com%22%2C%22user_uuid%22%3A%20%22a1f78c53-8647-40fb-a9ee-147b33d21c57%22%2C%22goalmaster%22%3A%20false%2C%22group_id%22%3A%203%2C%22admin_group_uuids%22%3A%20%5B%5D%2C%22manager_id%22%3A%20524%2C%22is_manager%22%3A%20false%2C%22org%22%3A%20%22BetterWorks%22%2C%22org_id%22%3A%201%2C%22org_uuid%22%3A%20%2224ec588c-7f63-4f9f-9c82-a634030c1e04%22%2C%22timezone%22%3A%20%22Asia%2FKolkata%22%2C%22is_super_admin%22%3A%20false%2C%22is_admin%22%3A%20false%2C%22is_group_admin%22%3A%20false%2C%22groupId%22%3A%20%2224ec588c-7f63-4f9f-9c82-a634030c1e04%22%2C%22locale%22%3A%20%22en%22%2C%22id%22%3A%20%221314%22%2C%22%24created%22%3A%20%222023-02-01T07%3A34%3A46.000Z%22%2C%22%24email%22%3A%20%22aakansha.srivastava%40betterworks.com%22%2C%22came_from%22%3A%20%22%2Fconversation%2F%22%2C%22__mps%22%3A%20%7B%7D%2C%22__mpso%22%3A%20%7B%7D%2C%22__mpus%22%3A%20%7B%7D%2C%22__mpa%22%3A%20%7B%7D%2C%22__mpu%22%3A%20%7B%7D%2C%22__mpr%22%3A%20%5B%5D%2C%22__mpap%22%3A%20%5B%5D%7D; _ga_KKJXED54QW=GS1.2.1721141997.26.1.1721141997.0.0.0; _gcl_au=1.1.4541294.1727273105; __hstc=195192115.7d7a0f61fec8025fde053c3eb3acc312.1727273107084.1727273107084.1727273107084.1; hubspotutk=7d7a0f61fec8025fde053c3eb3acc312; __hssrc=1; _CEFT=EgNwlgpg7hAmBcA7AhgewJoQJwGEBsAGgGoDWA0AFICeiMAsgLYBeA4gJJ1A; _biz_nA=9; _uetvid=2bae0d70a5e511ed96dc7b043a733e5e; _biz_pendingA=%5B%5D; cebsp_=5; __q_state_tnDN3QminTauEddA=eyJ1dWlkIjoiYjZhYzIyMzAtZWFjMS00MWY2LTg0YmYtZWQxODk5YWZiZjgzIiwiY29va2llRG9tYWluIjoiYmV0dGVyd29ya3MuY29tIiwibWVzc2VuZ2VyRXhwYW5kZWQiOmZhbHNlLCJwcm9tcHREaXNtaXNzZWQiOmZhbHNlLCJjb252ZXJzYXRpb25JZCI6IjE0OTEwMTg2NDI1NDE2MzM3NzMiLCJhY3RpdmVTZXNzaW9uSWQiOm51bGwsInNjcmlwdElkIjoiMTE0NTM2ODk0OTYyNDkxNDEzNCIsInN0YXRlQnlTY3JpcHRJZCI6eyIxMTQ1MzY4OTQ5NjI0OTE0MTM0Ijp7ImRpc21pc3NlZCI6ZmFsc2UsInNlc3Npb25JZCI6bnVsbH19fQ==; _ga_932QLKSSHL=GS1.1.1727275319.4.1.1727275320.0.0.0; _ce.s=v~f8cc39f7038b2c90788a00fb7fd749713f03e51c~lcw~1727275320707~lva~1706552721203~vpv~0~v11.fhb~1727273108372~v11.lhb~1727275319727~flvl~%2CnaoYe9C6XVk%3AJynweMmzGIM~v11.cs~433307~v11.s~2c0d5360-7b47-11ef-aca6-8d2e95815691~v11.sla~1727275320708~v11.send~1727275319704~gtrk.la~m1hz4n7m~lcw~1727275320709; _ga=GA1.2.1661079131.1692882786; sessionid=nxofe1vpuiiqpxg846yrtvctjvlyclkc; csrftoken=5Q2Tqo3yW7TfsWovPJIThDvR50WJ3vPP; _ga_9PJXZCVCXF=GS1.2.1730191432.13.0.1730191432.60.0.0; ajs_group_id=f3b58ecb-a150-49ca-afbc-ae1cb50ba786; ajs_user_id=22; ajs_anonymous_id=9709a004-499a-4569-a3c4-442969006ead',
    #     'Content-Type': 'application/json',
    #     'Referer': 'https://data-platform.teams.betterworks.com/.betterworks.com/'
    # }
    # headers = {
        
    #     'X-CSRFToken': 'QZxb0vTfLzaU1vk4EQOw26tIiZpeLyPA',
    #     'Authorization': "Token 7c5b2b81-46ae-43c8-9de6-d4a6b8246ae4",
    #     'Cookie': 'token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjJhZDcyMGJiLWE3ZDktNDkyMC1iMjM1LTJkYmYzYjYyZDg0MiJ9.3_4yQ0ozypW77SBngTF5DvvRsULWimlzDjNNwuVW3N8; sessionid=ezftx4ye6gcsqpuxzblypjkiuif3j1p2; csrftoken=QZxb0vTfLzaU1vk4EQOw26tIiZpeLyPA',
    #     'Content-Type': 'application/json',
    #     'Referer': 'http://localhost:9090/'
    # }

    headers = {
            
        'X-CSRFToken': 'W5SPQTW0tG6Nmz0S2ZHPXOxtUI6CpW4HURWIPqw3KXTtHMgSeGfPV0mPWkca4e9L',
        'Authorization': "Token 3ae40306-3b43-41f5-b91d-9de385618b85",
        'Cookie': 'first_visit_url=https://www.betterworks.com/; _mkto_trk=id:133-YCN-039&token:_mch-betterworks.com-1706552720607-92718; _biz_uid=1124676ba79f45d395c6599952f8d5a5; _ga_FD90Y8GQGR=GS1.2.1706552720.1.0.1706552720.60.0.0; _biz_flagsA=%7B%22Version%22%3A1%2C%22Mkto%22%3A%221%22%2C%22ViewThrough%22%3A%221%22%2C%22XDomain%22%3A%221%22%7D; _ce.irv=new; cebs=1; _vwo_uuid_v2=D900203F43D8E74B465515F1E8EDE5736|aca63d702358ce08f14bda79a2ba9c0d; mp_dddd49acc22c844b6f90427030f38120_mixpanel=%7B%22distinct_id%22%3A%20%22664329%22%2C%22%24device_id%22%3A%20%221905a1c9dff17cb-027e61cb4b412a-19525637-1d73c0-1905a1c9e0017cb%22%2C%22mp_lib%22%3A%20%22Segment%3A%20web%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%2C%22__mps%22%3A%20%7B%7D%2C%22__mpso%22%3A%20%7B%7D%2C%22__mpus%22%3A%20%7B%7D%2C%22__mpa%22%3A%20%7B%7D%2C%22__mpu%22%3A%20%7B%7D%2C%22__mpr%22%3A%20%5B%5D%2C%22__mpap%22%3A%20%5B%5D%2C%22%24user_id%22%3A%20%22664329%22%2C%22mp_name_tag%22%3A%20%22aakansha.srivastava%40betterworks.com%22%2C%22user_uuid%22%3A%20%2284e0593c-c29c-4a2e-b0d2-5a33e1099463%22%2C%22goalmaster%22%3A%20false%2C%22admin_group_uuids%22%3A%20%5B%0A%20%20%20%20%221242c72b-43f7-49dd-9716-5bad95c09edb%22%2C%0A%20%20%20%20%229a690fc3-3a67-4d62-a46a-cd8902dd19d9%22%0A%5D%2C%22manager_id%22%3A%20null%2C%22is_manager%22%3A%20false%2C%22org%22%3A%20%22BetterWorks%22%2C%22org_id%22%3A%201%2C%22org_uuid%22%3A%20%22403a44af-7d45-45e7-b460-ae5a912d76bb%22%2C%22timezone%22%3A%20%22Asia%2FKolkata%22%2C%22is_super_admin%22%3A%20false%2C%22is_admin%22%3A%20false%2C%22is_group_admin%22%3A%20false%2C%22groupId%22%3A%201%2C%22locale%22%3A%20%22en%22%2C%22id%22%3A%20%22664329%22%2C%22%24created%22%3A%20%222023-03-16T17%3A52%3A00.000Z%22%2C%22%24email%22%3A%20%22aakansha.srivastava%40betterworks.com%22%2C%22came_from%22%3A%20%22%2F%22%7D; _ga_KGTSTVSJX4=GS1.2.1719498744.1.1.1719498744.0.0.0; mp_1275c5d092aaec694b419c77e1cce879_mixpanel=%7B%22distinct_id%22%3A%20%22142855%22%2C%22%24device_id%22%3A%20%221905a1a824d1653-06d8df6558b974-19525637-1d73c0-1905a1a824d1654%22%2C%22mp_lib%22%3A%20%22Segment%3A%20web%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%2C%22__mps%22%3A%20%7B%7D%2C%22__mpso%22%3A%20%7B%7D%2C%22__mpus%22%3A%20%7B%7D%2C%22__mpa%22%3A%20%7B%7D%2C%22__mpu%22%3A%20%7B%7D%2C%22__mpr%22%3A%20%5B%5D%2C%22__mpap%22%3A%20%5B%5D%2C%22%24user_id%22%3A%20%22142855%22%2C%22mp_name_tag%22%3A%20%22aakansha.srivastava%40betterworks.com%22%2C%22user_uuid%22%3A%20%226e8e092b-f699-4602-bd13-91139dc98b6d%22%2C%22goalmaster%22%3A%20false%2C%22admin_group_uuids%22%3A%20%5B%5D%2C%22manager_id%22%3A%20null%2C%22is_manager%22%3A%20false%2C%22org%22%3A%20%22BetterWorks%22%2C%22org_id%22%3A%201%2C%22org_uuid%22%3A%20%228825b49a-a02b-4f8b-96da-2feb65bd3f96%22%2C%22timezone%22%3A%20%22Asia%2FKolkata%22%2C%22is_super_admin%22%3A%20false%2C%22is_admin%22%3A%20false%2C%22is_group_admin%22%3A%20false%2C%22groupId%22%3A%20%228825b49a-a02b-4f8b-96da-2feb65bd3f96%22%2C%22locale%22%3A%20%22en_GB%22%2C%22id%22%3A%20%22142855%22%2C%22%24created%22%3A%20%222023-07-25T11%3A18%3A12.000Z%22%2C%22%24email%22%3A%20%22aakansha.srivastava%40betterworks.com%22%2C%22came_from%22%3A%20%22%2F%22%7D; mp_dbaf4eb08ba45118434f514f698c36e7_mixpanel=%7B%22distinct_id%22%3A%20%221314%22%2C%22%24device_id%22%3A%20%2218a27ad575713f4-039b5add6d3a71-1a525634-1d73c0-18a27ad575713f4%22%2C%22mp_lib%22%3A%20%22Segment%3A%20web%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%2C%22%24user_id%22%3A%20%221314%22%2C%22mp_name_tag%22%3A%20%22aakansha.srivastava%40betterworks.com%22%2C%22user_uuid%22%3A%20%22a1f78c53-8647-40fb-a9ee-147b33d21c57%22%2C%22goalmaster%22%3A%20false%2C%22group_id%22%3A%203%2C%22admin_group_uuids%22%3A%20%5B%5D%2C%22manager_id%22%3A%20524%2C%22is_manager%22%3A%20false%2C%22org%22%3A%20%22BetterWorks%22%2C%22org_id%22%3A%201%2C%22org_uuid%22%3A%20%2224ec588c-7f63-4f9f-9c82-a634030c1e04%22%2C%22timezone%22%3A%20%22Asia%2FKolkata%22%2C%22is_super_admin%22%3A%20false%2C%22is_admin%22%3A%20false%2C%22is_group_admin%22%3A%20false%2C%22groupId%22%3A%20%2224ec588c-7f63-4f9f-9c82-a634030c1e04%22%2C%22locale%22%3A%20%22en%22%2C%22id%22%3A%20%221314%22%2C%22%24created%22%3A%20%222023-02-01T07%3A34%3A46.000Z%22%2C%22%24email%22%3A%20%22aakansha.srivastava%40betterworks.com%22%2C%22came_from%22%3A%20%22%2Fconversation%2F%22%2C%22__mps%22%3A%20%7B%7D%2C%22__mpso%22%3A%20%7B%7D%2C%22__mpus%22%3A%20%7B%7D%2C%22__mpa%22%3A%20%7B%7D%2C%22__mpu%22%3A%20%7B%7D%2C%22__mpr%22%3A%20%5B%5D%2C%22__mpap%22%3A%20%5B%5D%7D; _ga_KKJXED54QW=GS1.2.1721141997.26.1.1721141997.0.0.0; _gcl_au=1.1.4541294.1727273105; __hstc=195192115.7d7a0f61fec8025fde053c3eb3acc312.1727273107084.1727273107084.1727273107084.1; hubspotutk=7d7a0f61fec8025fde053c3eb3acc312; __hssrc=1; _CEFT=EgNwlgpg7hAmBcA7AhgewJoQJwGEBsAGgGoDWA0AFICeiMAsgLYBeA4gJJ1A; _biz_nA=9; _uetvid=2bae0d70a5e511ed96dc7b043a733e5e; _biz_pendingA=%5B%5D; cebsp_=5; __q_state_tnDN3QminTauEddA=eyJ1dWlkIjoiYjZhYzIyMzAtZWFjMS00MWY2LTg0YmYtZWQxODk5YWZiZjgzIiwiY29va2llRG9tYWluIjoiYmV0dGVyd29ya3MuY29tIiwibWVzc2VuZ2VyRXhwYW5kZWQiOmZhbHNlLCJwcm9tcHREaXNtaXNzZWQiOmZhbHNlLCJjb252ZXJzYXRpb25JZCI6IjE0OTEwMTg2NDI1NDE2MzM3NzMiLCJhY3RpdmVTZXNzaW9uSWQiOm51bGwsInNjcmlwdElkIjoiMTE0NTM2ODk0OTYyNDkxNDEzNCIsInN0YXRlQnlTY3JpcHRJZCI6eyIxMTQ1MzY4OTQ5NjI0OTE0MTM0Ijp7ImRpc21pc3NlZCI6ZmFsc2UsInNlc3Npb25JZCI6bnVsbH19fQ==; _ga_932QLKSSHL=GS1.1.1727275319.4.1.1727275320.0.0.0; _ce.s=v~f8cc39f7038b2c90788a00fb7fd749713f03e51c~lcw~1727275320707~lva~1706552721203~vpv~0~v11.fhb~1727273108372~v11.lhb~1727275319727~flvl~%2CnaoYe9C6XVk%3AJynweMmzGIM~v11.cs~433307~v11.s~2c0d5360-7b47-11ef-aca6-8d2e95815691~v11.sla~1727275320708~v11.send~1727275319704~gtrk.la~m1hz4n7m~lcw~1727275320709; _ga=GA1.2.1661079131.1692882786; _ga_9PJXZCVCXF=GS1.2.1730191432.13.0.1730191432.60.0.0; sessionid=vp11ml49dukhqgb4cj0bi76d5sd50rpq; csrftoken=8We39HKdrrXQvnqamRIa8mZwcMgIPsfe; ajs_user_id=269; ajs_anonymous_id=501724a5-5915-41a1-a34a-bbc1d22511bc; ajs_group_id=f3b58ecb-a150-49ca-afbc-ae1cb50ba786',
        'Content-Type': 'application/json',
        'Referer': 'https://rainforest.betterworks.com/'

    }
    response = requests.post(rainforest_api_url, json=payload, headers=headers)  # or however you're making the request
    response_data = response.json()
    print('response_data', response_data) # Convert the response to a dictionary
    output_data = response_data['output']
    suggestion_data = response_data['details']

    print(output_data)
    return output_data, suggestion_data
    # return response.json().get(["outputs"]['data'])

# Function to translate text back to English using Deep Translator
def back_translate(text, source_lang):
    try:
        # Create a translator instance with source and target languages
        translator = GoogleTranslator(source='auto', target='en')
        return translator.translate(text)
    except Exception as e:
        print(f"Translation error for {source_lang}: {e}")
        return ""

# Function to check meaning consistency using semantic similarity
def check_meaning_consistency(english_back_translated, back_translated_feedback):
    english_embedding = model.encode(english_back_translated)
    similarities = {}
    
    for idx, back_translated in enumerate(back_translated_feedback):
        other_embedding = model.encode(back_translated)
        cosine_similarity = util.pytorch_cos_sim(english_embedding, other_embedding).item()
        similarities[f'language_{idx+1}'] = cosine_similarity
    
    return similarities


# Initialize results list to store each row of data
results = []

# Main evaluation loop for each language
for lang, (feedback,lang_code) in supported_languages.items():
    print(f"Testing in {lang}...")

    # Get rephrased feedback
    rephrased_feedback = get_rephrased_feedback(feedback)

    print(f"Rephrased output: {rephrased_feedback}")

    # Back-translate to English
    back_translated_feedback = back_translate(rephrased_feedback[0], lang_code)
    back_translated_suggestions = back_translate(rephrased_feedback[1], lang_code)
    print(f"Back-translated to English: {back_translated_feedback}")

    # Append to results
    results.append({
        'Language': lang,
        'Input Feedback': feedback,
        'Output Feedback': rephrased_feedback[0],
        'Suggestions': rephrased_feedback[1],
        'Back-Translated Feedback': back_translated_feedback,
        'Back_Translated_Suggestions': back_translated_suggestions,
        'similarity_score': similarity_score 
    })

    df = pd.DataFrame(results)
    df.to_excel("multiLanguage/feedback_rephrasing_results_language.xlsx", index=False)

    # Check for meaning consistency using cosine similarity
    english_back_translated = "You're doing a good job, but there's room for improvement."
    similarity_score = check_meaning_consistency(english_back_translated, back_translated_feedback)
    results[-1]['Meaning Consistency Score'] = similarity_score

    # Determine if the meaning is consistent based on a threshold
    threshold = 0.7  # You can adjust this threshold
    consistent = all(score >= threshold for score in similarity_score.values())
    results[-1]['Meaning Consistency'] = "Yes" if consistent else "No"



print("Results saved to feedback_rephrasing_results.xlsx")

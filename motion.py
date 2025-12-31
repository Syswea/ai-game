import streamlit as st
import requests  # 新增：用于调用本地 API

# --- 配置：指向你本地穿透出来的公网 URL ---
# 注意：如果是 frp，通常是 "http://云服务器IP:端口/logic"
# 如果是 Cloudflare，通常是 "https://xxx.trycloudflare.com/logic"
API_ENDPOINT = "http://你的公网IP:你的映射端口/logic" 

st.set_page_config(page_title="海龟汤 AI 调试器", page_icon="🐢")
st.title("🐢 海龟汤 AI 调试后台")
st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = []

chat_container = st.container(height=600)
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if usr_input := st.chat_input("输入你的推论..."):
    with chat_container:
        st.chat_message("user").markdown(usr_input)
    
    st.session_state.messages.append({"role": "user", "content": usr_input})

    with st.spinner('AI 正在思考中...'):
        try:
            # 修改：这里不再调用本地的 get_ai_response，而是发送网络请求
            response = requests.post(
                API_ENDPOINT, 
                json={"usr_input": usr_input},
                timeout=120 # 大模型推理较慢，超时时间设长一点
            )
            if response.status_code == 200:
                answer = response.json().get("answer")
            else:
                answer = f"错误：后端返回状态码 {response.status_code}"
                
        except Exception as e:
            answer = f"错误：无法连接到本地后端。请检查穿透隧道是否开启。{str(e)}"

    with chat_container:
        with st.chat_message("assistant"):
            st.markdown(answer)
    
    st.session_state.messages.append({"role": "assistant", "content": answer})

with st.sidebar:
    st.header("调试设置")
    if st.button("清空对话"):
        st.session_state.messages = []
        st.rerun()
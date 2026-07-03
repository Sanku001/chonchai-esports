import streamlit as st
from tinydb import TinyDB, Query

# ตั้งค่าหน้าเว็บให้เป็นแบบ Wide เพื่อความสวยงามและกว้างขวาง
st.set_page_config(page_title="E-Sports Dashboard", page_icon="🏆", layout="wide")

# ==========================================
# ส่วนที่ 1: เตรียมฐานข้อมูล (TinyDB Setup)
# ==========================================
allowed_games = ("RoV", "Valorant", "FC Online")
db = TinyDB('esports_db.json')
TeamQuery = Query()

# ฟังก์ชันบันทึกข้อมูล
def register_team(team_name, game, members_list):
    if not team_name.strip():
        return False, "❌ กรุณากรอกชื่อทีม"
    if game not in allowed_games:
        return False, f"❌ ขออภัย ไม่มีการแข่งขันเกม {game}"
    if db.search(TeamQuery.team_name == team_name):
        return False, f"❌ ขออภัย ชื่อทีม '{team_name}' ถูกใช้ไปแล้ว"
    if len(members_list) < 3:
        return False, "❌ ขออภัย สมาชิกในทีมต้องมีอย่างน้อย 3 คน"
        
    db.insert({
        "team_name": team_name,
        "game": game,
        "members": members_list
    })
    return True, "🎉 ลงทะเบียนสำเร็จ!"


# ==========================================
# ส่วนที่ 2: ออกแบบหน้าเว็บหลัก (Beautiful Web UI)
# ==========================================
st.title("🏆 ระบบจัดการการแข่งขัน ชลชาย E-Sports")
st.write("แพลตฟอร์มสมัครแข่งและดูรายชื่อทีมแบบ Real-time")

# แยกหน้าจอเป็น 2 แท็บ: แท็บสมัครแข่งขัน และ แท็บดูรายชื่อทีม
tab_register, tab_dashboard = st.tabs(["📝 ฟอร์มลงทะเบียน", "📊 ตรวจสอบข้อมูลทีมแข่ง"])

# ------------------------------------------
# TAB 1: ฟอร์มลงทะเบียน
# ------------------------------------------
with tab_register:
    st.subheader("กรอกข้อมูลเพื่อส่งทีมของคุณเข้าแข่งขัน")
    
    with st.form(key="reg_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            t_name = st.text_input("🛡️ ชื่อทีม", placeholder="เช่น Chonชาย Slayer")
        with col2:
            t_game = st.selectbox("🎮 เลือกเกมที่จะลงแข่ง", allowed_games)
            
        members_raw = st.text_area(
            "👥 รายชื่อสมาชิกในทีม (พิมพ์ชื่อแยกกันด้วยเครื่องหมายคอมม่า `,`)",
            placeholder="เช่น: นายสมชาย ใจดี, นายสมศักดิ์ รักเรียน, นายสมปอง มุ่งมั่น (อย่างน้อย 3 คน)"
        )
        
        submit_btn = st.form_submit_button(label="🚀 ยืนยันการลงทะเบียน")

    if submit_btn:
        members = [m.strip() for m in members_raw.split(",") if m.strip()]
        is_success, message = register_team(t_name, t_game, members)
        if is_success:
            st.success(message)
            st.balloons() # เอฟเฟกต์ลูกโป่งฉลองความสำเร็จ!
        else:
            st.error(message)

# ------------------------------------------
# TAB 2: หน้าดูข้อมูลแบบสวยงาม (Dashboard)
# ------------------------------------------
with tab_dashboard:
    all_teams = db.all()
    
    if not all_teams:
        st.info("ℹ️ ปัจจุบันยังไม่มีทีมใดลงทะเบียนในระบบ สามารถไปที่แท็บ 'ฟอร์มลงทะเบียน' เพื่อเริ่มคนแรกได้เลย!")
    else:
        # 🟢 ส่วนที่ 2.1: สรุปยอด (Metrics Dashboard)
        st.subheader("📈 ภาพรวมการรับสมัคร")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        
        # นับจำนวนทีมแยกตามเกม
        total_teams = len(all_teams)
        rov_count = len([t for t in all_teams if t['game'] == 'RoV'])
        val_count = len([t for t in all_teams if t['game'] == 'Valorant'])
        fc_count = len([t for t in all_teams if t['game'] == 'FC Online'])
        
        m_col1.metric(label="🎬 ทีมสมัครทั้งหมด", value=f"{total_teams} ทีม")
        m_col2.metric(label="⚔️ RoV", value=f"{rov_count} ทีม")
        m_col3.metric(label="🎯 Valorant", value=f"{val_count} ทีม")
        m_col4.metric(label="⚽ FC Online", value=f"{fc_count} ทีม")
        
        st.markdown("---")
        
        # 🟢 ส่วนที่ 2.2: แสดงการ์ดข้อมูลทีม (Grid Layout Cards)
        st.subheader("🛡️ รายชื่อทีมและสมาชิกทั้งหมด")
        
        # กำหนดให้แสดงผล 3 คอลัมน์ต่อหนึ่งแถว (ปรับให้เข้ากับหน้าจอคอมพิวเตอร์)
        grid_cols = st.columns(3)
        
        # วนลูปสร้างการ์ดสวยๆ ให้แต่ละทีม
        for idx, team in enumerate(all_teams):
            # ใช้การหารเอาเศษ (Modulo) เพื่อสลับคอลัมน์ไปเรื่อยๆ 0, 1, 2, 0, 1, 2
            with grid_cols[idx % 3]:
                # st.container(border=True) จะสร้างกล่องสี่เหลี่ยมคล้าย Card สวยงาม
                with st.container(border=True):
                    # หัวการ์ดแสดงชื่อทีม
                    st.markdown(f"### 🛡️ {team['team_name']}")
                    
                    # แสดงแท็กเกมตามประเภท (ใส่สี/ไอคอนให้ต่างกัน)
                    game_icon = "⚔️" if team['game'] == "RoV" else "🎯" if team['game'] == "Valorant" else "⚽"
                    st.markdown(f"**เกมที่แข่ง:** `{game_icon} {team['game']}`")
                    
                    st.markdown("**สมาชิกในทีม:**")
                    # วนลูปรายชื่อสมาชิกแบบ List สวยๆ
                    for m_idx, member in enumerate(team['members'], 1):
                        st.markdown(f"{m_idx}. 👤 {member}")
                        
        # 🟢 ส่วนที่ 2.3: โซนผู้ดูแลระบบ (ปุ่มลบข้อมูล)
        st.markdown("---")
        with st.expander("⚙️ โซนผู้ดูแลระบบ (Admin Only)"):
            st.warning("คำเตือน: การกดปุ่มด้านล่างจะลบข้อมูลถาวรออกจากไฟล์ JSON")
            if st.button("🗑️ ล้างฐานข้อมูลทั้งหมด", type="primary"):
                db.truncate()
                st.success("เคลียร์ฐานข้อมูลเรียบร้อย!")
                st.rerun()
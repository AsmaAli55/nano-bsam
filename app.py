import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# إعدادات الصفحة والهوية البصرية للبرنامج
st.set_page_config(page_title="Nano-BSAM Assessment Tool", layout="wide")

# --- بيانات النموذج العلمي الثابتة (أوزان الخبراء - الباب الثالث) ---
REF_WEIGHTS = {
    'Environmental': 0.3427, 'Economic': 0.2774,
    'Technical': 0.2337, 'Social': 0.1462
}

INDICATORS_DATA = [
    # المعايير البيئية
    {'cat': 'Environmental', 'code': 'E.1', 'name': 'البصمة الكربونية (ECC)', 'w_global': 0.0521,
     'desc': 'معامل الكربون المتجسد كجم CO2/كجم'},
    {'cat': 'Environmental', 'code': 'E.2', 'name': 'المحتوى المعاد تدويره', 'w_global': 0.0345,
     'desc': 'نسبة المواد المعاد تدويرها من الكتلة الكلية'},
    {'cat': 'Environmental', 'code': 'E.3', 'name': 'كفاءة الطاقة المتجسدة', 'w_global': 0.0870,
     'desc': 'كثافة الطاقة المتجسدة MJ/kg'},
    {'cat': 'Environmental', 'code': 'E.4', 'name': 'استهلاك الموارد المائية', 'w_global': 0.0542,
     'desc': 'كثافة المياه المتجسدة وطبيعة النظام'},
    {'cat': 'Environmental', 'code': 'E.5', 'name': 'جودة الهواء (VOCs)', 'w_global': 0.0643,
     'desc': 'معدل انبعاثات المركبات العضوية المتطايرة'},
    {'cat': 'Environmental', 'code': 'E.6', 'name': 'المصدر الطبيعي والمتجدد', 'w_global': 0.0506,
     'desc': 'نسبة المكونات المتجددة في المادة'},
    # المعايير الاقتصادية
    {'cat': 'Economic', 'code': 'C.1', 'name': 'التكلفة الأولية', 'w_global': 0.0611,
     'desc': 'تكلفة التوريد والتركيب للمتر المربع'},
    {'cat': 'Economic', 'code': 'C.2', 'name': 'تكلفة الطاقة التشغيلية', 'w_global': 0.0916,
     'desc': 'الوفر في فواتير الكهرباء (محاكاة)'},
    {'cat': 'Economic', 'code': 'C.3', 'name': 'تكلفة الصيانة', 'w_global': 0.0820,
     'desc': 'عدد دورات الصيانة والتنظيف الذاتي'},
    {'cat': 'Economic', 'code': 'C.4', 'name': 'تكلفة النقل', 'w_global': 0.0205,
     'desc': 'تأثير الوزن والمسافة على تكلفة اللوجستيات'},
    {'cat': 'Economic', 'code': 'C.5', 'name': 'تكلفة التخلص والاسترداد', 'w_global': 0.0223,
     'desc': 'إمكانية الفك (DfD) وإعادة البيع خردة'},
    # المعايير التقنية
    {'cat': 'Technical', 'code': 'T.1', 'name': 'المتانة والعمر الافتراضي', 'w_global': 0.0406,
     'desc': 'عدد سنوات بقاء المادة دون تدهور'},
    {'cat': 'Technical', 'code': 'T.2', 'name': 'المرونة وخفة الوزن', 'w_global': 0.0133,
     'desc': 'كفاءة الكتلة وتقليل الأحمال الإنشائية'},
    {'cat': 'Technical', 'code': 'T.3', 'name': 'سهولة الصيانة', 'w_global': 0.0307,
     'desc': 'وجود وصلات عكسية ميكانيكية للإحلال'},
    {'cat': 'Technical', 'code': 'T.4', 'name': 'مقاومة العوامل الجوية', 'w_global': 0.0366,
     'desc': 'القدرة على طرد المياه وحماية الطبقات'},
    {'cat': 'Technical', 'code': 'T.5', 'name': 'مقاومة الحريق', 'w_global': 0.0360,
     'desc': 'زمن صمود المادة بالدقائق (FRR)'},
    {'cat': 'Technical', 'code': 'T.6', 'name': 'الراحة الحرارية', 'w_global': 0.0382,
     'desc': 'تحقيق قيم R و U المطلوبة كودياً'},
    {'cat': 'Technical', 'code': 'T.7', 'name': 'الراحة الضوئية', 'w_global': 0.0206,
     'desc': 'معامل نفاذية الضوء وجودة الإضاءة'},
    {'cat': 'Technical', 'code': 'T.8', 'name': 'العزل الصوتي', 'w_global': 0.0177, 'desc': 'معامل خفض الضوضاء (Rw)'},
    # المعايير الاجتماعية
    {'cat': 'Social', 'code': 'S.1', 'name': 'التوافق مع التراث', 'w_global': 0.0241,
     'desc': 'مدى ملاءمة المظهر للثقافة المعمارية'},
    {'cat': 'Social', 'code': 'S.2', 'name': 'الجمال واستدامة المظهر', 'w_global': 0.0249,
     'desc': 'الحفاظ على الصورة البصرية للواجهة'},
    {'cat': 'Social', 'code': 'S.3', 'name': 'توفر المادة محلياً', 'w_global': 0.0279,
     'desc': 'نسبة المكون المحلي ودعم الصناعة الوطنية'},
    {'cat': 'Social', 'code': 'S.4', 'name': 'توفر العمالة الماهرة', 'w_global': 0.0266,
     'desc': 'الحاجة لخبراء أجانب مقابل فنيين محليين'},
    {'cat': 'Social', 'code': 'S.5', 'name': 'السلامة والأمان', 'w_global': 0.0428,
     'desc': 'خلو المادة من السمية وسهولة المناولة'},
]

# قيم الأداء المرجعية الافتراضية للبديل التقليدي (BM) المستخرجة من مصفوفات الباب الرابع لرسالتكِ
BM_DEFAULT_SCORES = {
    'E.1': 5.5, 'E.2': 2.5, 'E.3': 5.5, 'E.4': 2.5, 'E.5': 4.5, 'E.6': 3.5,
    'C.1': 6.0, 'C.2': 1.0, 'C.3': 2.5, 'C.4': 7.0, 'C.5': 7.0,
    'T.1': 3.0, 'T.2': 3.0, 'T.3': 2.5, 'T.4': 2.5, 'T.5': 4.5, 'T.6': 1.0, 'T.7': 2.5, 'T.8': 6.0,
    'S.1': 5.5, 'S.2': 2.5, 'S.3': 7.0, 'S.4': 6.0, 'S.5': 3.5
}

# قيم الأداء الافتراضية للبديل النانوي (NM) المستخرجة من مصفوفات الباب الرابع لرسالتكِ
NM_DEFAULT_SCORES = {
    'E.1': 4.0, 'E.2': 7.5, 'E.3': 4.0, 'E.4': 7.0, 'E.5': 4.5, 'E.6': 6.0,
    'C.1': 3.5, 'C.2': 9.0, 'C.3': 7.5, 'C.4': 2.5, 'C.5': 2.5,
    'T.1': 6.5, 'T.2': 7.0, 'T.3': 7.5, 'T.4': 7.5, 'T.5': 5.5, 'T.6': 9.0, 'T.7': 7.5, 'T.8': 3.5,
    'S.1': 4.0, 'S.2': 7.5, 'S.3': 2.5, 'S.4': 3.5, 'S.5': 6.5
}

st.title("🏗️ نظام المنظومة الحاسوبية المتكاملة لنموذج (Nano-BSAM)")
st.write("أداة منهجية تفاعلية شاملة للمفاضلة بين المواد وتقييم جدارتها الاستدامية في مشروعات العاصمة الإدارية")

tab1, tab2 = st.tabs(["📝 1. مدخلات تقييم المواد (مسطرة 1-9)", "📊 2. حساب النتائج وتحليل الحساسية"])

with tab1:
    st.header("تعديل درجات تقييم البدائل بناءً على مساطر القياس الفنية:")
    st.info(
        "مقياس ساعتي المعتمد في الأطروحة: 9 = تميز ابتكاري ومستدام مطلق، 5 = امتثال تام للكود المرجعي، 1 = أداء سلبي حرج.")

    col_nm, col_bm = st.columns(2)

    with col_nm:
        st.subheader("🔬 تقييم الغلاف النانوي المقترح (NM)")
        nm_user_scores = {}
        for ind in INDICATORS_DATA:
            nm_user_scores[ind['code']] = st.slider(
                f"{ind['code']}: {ind['name']} (NM)", 1.0, 9.0, NM_DEFAULT_SCORES[ind['code']], step=0.5,
                help=ind['desc']
            )

    with col_bm:
        st.subheader("🧱 تقييم غلاف المبنى التقليدي المرجعي (BM)")
        bm_user_scores = {}
        for ind in INDICATORS_DATA:
            bm_user_scores[ind['code']] = st.slider(
                f"{ind['code']}: {ind['name']} (BM)", 1.0, 9.0, BM_DEFAULT_SCORES[ind['code']], step=0.5,
                help=ind['desc']
            )

with tab2:
    # شريط التحكم الجانبي لتحليل الحساسية
    st.sidebar.header("⚙️ تحليل الحساسية الديناميكي")
    st.sidebar.write("قم بتعديل أوزان المحاور الرئيسية لاختبار رصانة واستقرار القرار ضد التذبذب:")
    sens_env = st.sidebar.slider("الوزن البيئي (EC)", 0.0, 1.0, REF_WEIGHTS['Environmental'], step=0.01)
    sens_eco = st.sidebar.slider("الوزن الاقتصادي (CC)", 0.0, 1.0, REF_WEIGHTS['Economic'], step=0.01)
    sens_tech = st.sidebar.slider("الوزن التقني (TC)", 0.0, 1.0, REF_WEIGHTS['Technical'], step=0.01)
    sens_soc = st.sidebar.slider("الوزن الاجتماعي (SC)", 0.0, 1.0, REF_WEIGHTS['Social'], step=0.01)

    # تسوية الأوزان (Normalization)
    sum_w = sens_env + sens_eco + sens_tech + sens_soc
    w_adj = {
        'Environmental': sens_env / sum_w, 'Economic': sens_eco / sum_w,
        'Technical': sens_tech / sum_w, 'Social': sens_soc / sum_w
    } if sum_w > 0 else REF_WEIGHTS

    # الحسابات الرياضية للمؤشر النهائي
    nm_final_score, bm_final_score = 0, 0
    nm_cat_scores = {'Environmental': 0, 'Economic': 0, 'Technical': 0, 'Social': 0}
    bm_cat_scores = {'Environmental': 0, 'Economic': 0, 'Technical': 0, 'Social': 0}
    cat_counts = {'Environmental': 6, 'Economic': 5, 'Technical': 8, 'Social': 5}

    for ind in INDICATORS_DATA:
        nm_local_pref = nm_user_scores[ind['code']] / 9.0
        bm_local_pref = bm_user_scores[ind['code']] / 9.0

        original_cat_w = REF_WEIGHTS[ind['cat']]
        adjusted_ind_w = (ind['w_global'] / original_cat_w) * w_adj[ind['cat']]

        nm_final_score += adjusted_ind_w * nm_local_pref
        bm_final_score += adjusted_ind_w * bm_local_pref

        nm_cat_scores[ind['cat']] += nm_local_pref * (ind['w_global'] / original_cat_w)
        bm_cat_scores[ind['cat']] += bm_local_pref * (ind['w_global'] / original_cat_w)

    # عرض مؤشر جدارة الاستدامة الكلي
    total_combined = nm_final_score + bm_final_score
    nm_percentage = (nm_final_score / total_combined) * 100 if total_combined > 0 else 50.0
    bm_percentage = (bm_final_score / total_combined) * 100 if total_combined > 0 else 50.0

    res_col1, res_col2 = st.columns(2)
    res_col1.metric("🏆 مؤشر جدارة الاستدامة للغلاف النانوي (NM)", f"{nm_percentage:.2f}%")
    res_col2.metric("🧱 مؤشر جدارة الاستدامة للغلاف التقليدي (BM)", f"{bm_percentage:.2f}%")

    # 1. الرسم البياني الراداري (الأبعاد الأربعة)
    st.subheader("📈 بصمة الاستدامة التفصيلية عبر المحاور الأربعة (Radar Analysis)")
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=[nm_cat_scores['Environmental'] * 100, nm_cat_scores['Economic'] * 100, nm_cat_scores['Technical'] * 100,
           nm_cat_scores['Social'] * 100],
        theta=['البيئي', 'الاقتصادي', 'التقني', 'الاجتماعي'], fill='toself', name='الغلاف النانوي (NM)',
        line=dict(color='blue')
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=[bm_cat_scores['Environmental'] * 100, bm_cat_scores['Economic'] * 100, bm_cat_scores['Technical'] * 100,
           bm_cat_scores['Social'] * 100],
        theta=['البيئي', 'الاقتصادي', 'التقني', 'الاجتماعي'], fill='toself', name='الغلاف التقليدي (BM)',
        line=dict(color='red')
    ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True,
                            template="plotly_white")
    st.plotly_chart(fig_radar, use_container_width=True)

    # 2. رسم الأعمدة للمفاضلة الكلية
    st.subheader("📊 المقارنة الإجمالية للمفاضلة والقرار النهائي")
    fig_bar = go.Figure(data=[
        go.Bar(name='الغلاف النانوي (NM)', x=['مؤشر الاستدامة الكلي'], y=[nm_percentage / 100], marker_color='blue'),
        go.Bar(name='الغلاف التقليدي (BM)', x=['مؤشر الاستدامة الكلي'], y=[bm_percentage / 100], marker_color='red')
    ])
    fig_bar.update_layout(barmode='group', yaxis_range=[0, 1], template="plotly_white")
    st.plotly_chart(fig_bar, use_container_width=True)

    # كتابة التقرير التلقائي للقرار
    if nm_percentage > bm_percentage:
        st.success(
            f"القرار معتمد: **الغلاف النانوي (NM) يحقق الأداء الأمثل** ويتفوق بفارق صدارة شاسع يبلغ **{(nm_percentage - bm_percentage):.2f}%** تحت معايير التصميم الحالية.")
    else:
        st.warning(
            f"تحذير: **الغلاف التقليدي (BM) يتفوق** بمقدار **{(bm_percentage - nm_percentage):.2f}%**. يرجى إعادة مراجعة نسب ومكونات المواد النانوية.")

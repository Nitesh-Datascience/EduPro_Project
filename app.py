@st.cache_data(show_spinner='Preparing learner intelligence…')
def data():
    users,courses,tx=load_data()
    profiles=build_profiles(users,courses,tx)
    active,metrics=fit_segments(profiles)
    return users,courses,tx,profiles,active,metrics
try: users,courses,tx,profiles,active,metrics=data()
except Exception as exc: st.error(f'Could not load project data: {exc}');st.stop()
with st.sidebar:
    st.markdown('<div class="brand"><span class="icon">✧</span><b>EduPro <em>AI</em></b><small>NEURAL LEARNING INTELLIGENCE</small></div>',unsafe_allow_html=True)
    page=st.radio('NAVIGATION',['Overview','Learner Explorer','Recommendations','Segment Comparison','Model Comparison','Model & Data'],label_visibility='collapsed')
    st.markdown(f'<div class="sidebar-foot">● DATA READY &nbsp; · &nbsp; {len(tx):,} enrollments</div>',unsafe_allow_html=True)
st.markdown(f'<div class="hero"><small>✧ EDUPRO / AI PERSONALIZATION ENGINE</small><h1>{page}</h1><p>Understand every learner. Discover patterns. Recommend a smarter next step.</p></div>',unsafe_allow_html=True)
st.markdown('<div style="display:flex;gap:9px;flex-wrap:wrap;margin:-7px 0 20px;color:#8eabc1;font-size:10px;letter-spacing:.08em"><span style="padding:6px 10px;border:1px solid #285b5b;border-radius:30px;background:#102b2a;color:#71f2d4">● AI ENGINE READY</span><span style="padding:6px 10px;border:1px solid #344c68;border-radius:30px;background:#111f32">◈ BEHAVIOR ANALYTICS</span><span style="padding:6px 10px;border:1px solid #344c68;border-radius:30px;background:#111f32">✧ 3D LEARNER SPACE</span></div>',unsafe_allow_html=True)
def cards(items):
    cols=st.columns(len(items))
    for col,(label,value,note,color) in zip(cols,items):
        col.markdown(f'<div class="card" style="--accent:{color}"><div class="label">{label}</div><div class="value">{value}</div><div class="note">{note}</div></div>',unsafe_allow_html=True)
def chart(fig):
    existing_height=fig.layout.height or 350
    existing_margin=fig.layout.margin
    margin=dict(l=existing_margin.l if existing_margin.l is not None else 48,
                r=existing_margin.r if existing_margin.r is not None else 24,
                t=existing_margin.t if existing_margin.t is not None else 55,
                b=existing_margin.b if existing_margin.b is not None else 48)
    fig.update_layout(paper_bgcolor='#141f30',plot_bgcolor='#141f30',font=dict(family='Inter, sans-serif',size=11,color='#b7c9dc'),
        margin=margin,legend_title_text='',height=existing_height,
        title_font=dict(size=15,color='#ecf5ff'),hoverlabel=dict(bgcolor='#20344a',font_color='white'))
    fig.update_xaxes(gridcolor='#273a50',zeroline=False,title_font_size=11,tickfont_size=10)
    fig.update_yaxes(gridcolor='#273a50',zeroline=False,title_font_size=11,tickfont_size=10)
    st.plotly_chart(fig,width='stretch',theme=None)
if page=='Overview':
    cards([('TOTAL LEARNERS',f'{len(users):,}','Registered profiles','#42d9f4'),('ACTIVE LEARNERS',f'{len(active):,}','At least one enrollment','#29e5a2'),('COURSES',str(len(courses)),'Available catalog','#ffbd55'),('LEARNER SEGMENTS',str(metrics['selected_k']),'Selected by silhouette','#c18cff')])
    st.write('')
    cards([('TOTAL ENROLLMENTS',f'{len(tx):,}','Recorded course purchases','#29e5a2'),('COURSE CATEGORIES',str(courses.CourseCategory.nunique()),'Catalog domains','#e751ab'),('AVG COURSES / LEARNER',f'{len(tx)/len(users):.1f}','Transactions per profile','#42d9f4'),('SEGMENT QUALITY',f"{metrics['silhouette']:.3f}",'Silhouette score','#ffbd55')])
    a,b=st.columns([1.55,1],gap='medium')
    with a:
        heading,mode=st.columns([2,1])
        heading.subheader('Learner landscape')
        view=mode.segmented_control('Projection',['3D','2D'],default='3D',label_visibility='collapsed')
        colors={name:col for name,col in zip(sorted(active.segment.unique()),['#79d9ff','#b583ff','#42e9b8','#ffbd60','#f078b6','#6de0dc'])}
        sample=active.sample(n=min(1600,len(active)),random_state=42)
        if view=='3D':
            fig=px.scatter_3d(sample,x='x',y='y',z='z',color='segment',color_discrete_map=colors,
                hover_data=['UserID','preferred_category','enrollments'],opacity=.73,
                title='Explore learner clusters in 3D',labels={'x':'Behavior 1','y':'Behavior 2','z':'Behavior 3'})
            fig.update_traces(marker=dict(size=4.2,line=dict(width=.35,color='#d8ffff'),opacity=.82))
            fig.update_layout(height=455,margin=dict(l=0,r=0,t=48,b=0),
                legend=dict(orientation='h',y=-.04,x=0,font_size=10,bgcolor='rgba(10,20,34,.55)'),
                scene=dict(
                    bgcolor='#111d30',
                    xaxis=dict(title='Behavior dimension 1',backgroundcolor='#111d30',gridcolor='#38516a',showbackground=True,zerolinecolor='#4b7187',showspikes=False),
                    yaxis=dict(title='Behavior dimension 2',backgroundcolor='#111d30',gridcolor='#38516a',showbackground=True,zerolinecolor='#4b7187',showspikes=False),
                    zaxis=dict(title='Behavior dimension 3',backgroundcolor='#111d30',gridcolor='#38516a',showbackground=True,zerolinecolor='#4b7187',showspikes=False),
                    camera=dict(eye=dict(x=1.55,y=1.55,z=1.05)),
                    aspectmode='cube'))
        else:
            fig=px.scatter(sample,x='x',y='y',color='segment',color_discrete_map=colors,
                hover_data=['UserID','preferred_category','enrollments'],opacity=.65,
                title='Behavioral profile projection',labels={'x':'Behavior axis 1','y':'Behavior axis 2'})
            fig.update_traces(marker=dict(size=6,line=dict(width=0)))
            fig.update_layout(height=425,legend=dict(orientation='h',y=-.3,x=0,font_size=10),margin=dict(l=48,r=16,t=55,b=95))
        chart(fig)
        st.caption('✧ AI learner-space projection · drag to rotate · scroll to zoom · each point represents one learner')
    with b:
        st.subheader('Segment mix')
        mix=active.segment.value_counts().rename_axis('segment').reset_index(name='count')
        fig=px.bar(mix,x='count',y='segment',orientation='h',color='segment',color_discrete_map=colors,
            text='count',title='Learners by segment')
        fig.update_traces(textposition='outside',marker_line_width=0,showlegend=False)
        fig.update_layout(height=425,showlegend=False,margin=dict(l=170,r=65,t=55,b=46),bargap=.5)
        fig.update_xaxes(title_text='',tickformat=',d',showgrid=True)
        fig.update_yaxes(title_text='',automargin=True,categoryorder='total ascending')
        chart(fig)
    st.subheader('Enrollment activity monitor')
    dated=tx.dropna(subset=['TransactionDate']).copy()
    dated['weekday']=pd.Categorical(dated.TransactionDate.dt.day_name(),categories=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],ordered=True)
    dated['month']=dated.TransactionDate.dt.to_period('M').astype(str)
    heat=dated.groupby(['weekday','month'],observed=False).size().reset_index(name='enrollments')
    fig=px.density_heatmap(heat,x='month',y='weekday',z='enrollments',color_continuous_scale=[[0,'#172036'],[.3,'#263780'],[.65,'#18bca4'],[1,'#f6bd4f']],title='Day of week × month enrollment heatmap',labels={'month':'Enrollment month','weekday':'Day','enrollments':'Enrollments'})
    fig.update_layout(height=350,margin=dict(l=96,r=18,t=55,b=58),coloraxis_colorbar=dict(title='Enrollments',len=.75,thickness=11))
    fig.update_xaxes(title_text='',tickangle=-30)
    fig.update_yaxes(title_text='',categoryorder='array',categoryarray=['Sunday','Saturday','Friday','Thursday','Wednesday','Tuesday','Monday'])
    chart(fig)
    a,b=st.columns([1.4,1])
    with a:
        trend=dated.groupby('month').size().reset_index(name='enrollments')
        chart(px.line(trend,x='month',y='enrollments',markers=True,title='Enrollment trend'))
    with b:
        chart(px.bar(tx.CourseCategory.value_counts().reset_index().head(8),x='count',y='CourseCategory',orientation='h',title='Most enrolled course categories'))
elif page=='Learner Explorer':
    id=st.selectbox('Select learner ID',active.UserID.tolist())
    p=active.set_index('UserID').loc[id]
    cards([('SEGMENT',str(p.segment),'Behavior-based assignment','#29e5a2'),('ENROLLMENTS',int(p.enrollments),'Recorded transactions','#42d9f4'),('CATEGORIES',int(p.diversity),'Domains explored','#ffbd55'),('AVERAGE SPEND',f'₹{p.avg_spend:,.0f}','Per enrollment, workbook units','#c18cff')])
    st.subheader('Learning profile')
    st.write(f"**Preferred category:** {p.preferred_category}  ·  **Preferred level:** {p.preferred_level}  ·  **Average enrolled course rating:** {p.avg_rating:.2f}/5")
    history=tx.loc[tx.UserID==id,['TransactionDate','CourseName','CourseCategory','CourseLevel','Amount']].sort_values('TransactionDate',ascending=False)
    st.dataframe(history,width='stretch',hide_index=True)
elif page=='Recommendations':
    id=st.selectbox('Learner',active.UserID.tolist())
    a,b=st.columns(2)
    cat=a.selectbox('Category',['All',*sorted(courses.CourseCategory.unique())]); level=b.selectbox('Level',['All',*sorted(courses.CourseLevel.unique())])
    p=active.set_index('UserID').loc[id]
    st.info(f"**{p.segment}** · Interested in {p.preferred_category} · Typical level: {p.preferred_level}")
    results=recommend(id,active,courses,tx,category=None if cat=='All' else cat,level=None if level=='All' else level)
    if results.empty: st.warning('No unseen courses match these filters.')
    else:
        for _,c in results.iterrows():
            with st.container(border=True):
                left,right=st.columns([4,1]);left.markdown(f"### {c.CourseName}");left.caption(f"{c.CourseCategory} · {c.CourseLevel} · {c.CourseType} · ⭐ {c.CourseRating:.2f}");left.write(c['why']);right.metric('Match',f"{c.score:.0f}/100")
    st.caption('Scores rank catalog courses using category and level match, segment popularity, and smoothed rating. They do not measure learning outcomes.')
elif page=='Segment Comparison':
    summary=active.groupby('segment').agg(learners=('UserID','size'),enrollments=('enrollments','mean'),categories=('diversity','mean'),mean_spend=('avg_spend','mean'),mean_rating=('avg_rating','mean'),paid_share=('paid_share','mean')).round(2)
    st.dataframe(summary,width='stretch')
    metric=st.selectbox('Compare segments by',list(summary.columns[1:]))
    chart(px.bar(summary.reset_index(),x='segment',y=metric,color='segment',title=f'Average {metric.replace("_"," ")} by segment'))
    st.subheader('Most common interest by segment')
    st.dataframe(active.groupby('segment').preferred_category.agg(lambda x:x.value_counts().index[0]).rename('Top category'),width='stretch')
elif page=='Model Comparison':
    st.subheader('13 model benchmark')
    comparison_path=__import__('pathlib').Path(__file__).resolve().parent/'artifacts/model_comparison.csv'
    metadata_path=comparison_path.with_name('comparison_metadata.json')
    if not comparison_path.exists() or not metadata_path.exists():
        st.info('Run `python compare_models.py` to generate this benchmark.')
    else:
        import json
        comparison=pd.read_csv(comparison_path)
        meta=json.loads(metadata_path.read_text())
        st.caption(f"{meta['eligible_learners']:,} eligible learners · {meta['train_learners']:,} training · {meta['test_learners']:,} held out · {meta['target_classes']} categories")
        st.warning('Different tasks require different metrics: classification uses macro F1 (higher is better), regression uses MAE (lower is better), and anomaly models show unlabeled flag rates only.')
        for task in comparison.task.unique():
            part=comparison[comparison.task==task].copy()
            st.markdown(f'### {task}')
            st.dataframe(part.drop(columns=['task']).fillna('—'),width='stretch',hide_index=True)
            chart(px.bar(part,x='model',y='score',color='model',title=f"{task} · {part.metric.iloc[0]}"))
        st.caption('This workbook contains no learning outcomes, completion labels, or verified anomalies. These benchmarks must not be interpreted as course success or fraud detection.')
else:
    st.subheader('Model evaluation')
    cards([('SILHOUETTE',f"{metrics['silhouette']:.3f}",'Higher is better','#29e5a2'),('HIERARCHICAL AGREEMENT',f"{metrics['hierarchical_ari_sample']:.3f}",'Adjusted Rand index · sample of 500','#42d9f4')])
    chart(px.line(pd.DataFrame([{'k':k,'silhouette':v} for k,v in metrics['silhouette_by_k'].items()]),x='k',y='silhouette',markers=True,title='Cluster count selection'))
    st.write('**Data:** Users, Courses, Transactions. Only users with enrollments enter clustering; inactive users remain in the registered total.')
    st.write('**Limitations:** The workbook contains enrollment transactions but no completion, learning outcomes, impressions, or recommendation clicks. Recommendation precision and engagement lift require future logged outcomes or an A/B test; neither is claimed here.')
    st.download_button('Download learner segment assignments',active.drop(columns=['Email']).to_csv(index=False).encode(),'edupro_segments.csv','text/csv')

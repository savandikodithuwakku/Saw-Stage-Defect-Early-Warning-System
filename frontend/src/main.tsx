import { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Activity, AlertTriangle, CheckCircle2, Search, ShieldCheck } from 'lucide-react';
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import './styles.css';

const API = 'http://127.0.0.1:8001/api';
type Data = any;
const fetchApi = (path: string) => fetch(`${API}${path}`).then((response) => {
  if (!response.ok) throw new Error('API unavailable');
  return response.json();
});

function App() {
  const [page, setPage] = useState<'Overview' | 'Product Investigation' | 'Model Performance'>('Overview');
  const [overview, setOverview] = useState<Data>();
  const [metrics, setMetrics] = useState<Data>();
  const [products, setProducts] = useState<Data[]>([]);
  const [features, setFeatures] = useState<Data[]>([]);
  const [product, setProduct] = useState<Data>();
  const [productId, setProductId] = useState('');
  const [error, setError] = useState(false);

  useEffect(() => {
    Promise.all(['/overview', '/benchmark/metrics', '/benchmark/products', '/model-features'].map(fetchApi))
      .then(([overviewData, metricsData, productsData, featureData]) => {
        setOverview(overviewData);
        setMetrics(metricsData);
        setProducts(productsData);
        setFeatures(featureData);
      })
      .catch(() => setError(true));
  }, []);

  const investigate = (id = productId) => {
    const selectedId = id.trim() || products[0]?.product_id;
    if (!selectedId) return;
    setProductId(selectedId);
    fetchApi(`/investigation/${selectedId}`).then(setProduct).catch(() => setProduct(undefined));
  };

  const openInvestigation = () => {
    setPage('Product Investigation');
    if (!product && products[0]) investigate(products[0].product_id);
  };

  const nav = ['Overview', 'Product Investigation', 'Model Performance'] as const;
  return <div className="shell">
    <aside>
      <div className="brand"><div className="brand-mark"><Activity size={19} /></div><div><strong>Sawing Process Quality Intelligence</strong></div></div>
      <nav>{nav.map((item) => <button className={page === item ? 'active' : ''} onClick={() => setPage(item)} key={item}>{item}</button>)}</nav>
    </aside>
    <main>
      <header><div><h1>{page}</h1></div></header>
      <div className="content">
        {error ? <div className="trust-banner"><AlertTriangle size={22} /><div><strong>Could not load the dashboard data</strong><p>Start FastAPI on port 8001, then reload this page.</p></div></div> : !overview ? <div className="loading">Loading final model data...</div> : <>
          {page === 'Overview' && <Overview data={overview} onInvestigate={openInvestigation} />}
          {page === 'Product Investigation' && <Investigation products={products} productId={productId} setProductId={setProductId} product={product} investigate={investigate} />}
          {page === 'Model Performance' && <Performance features={features} />}
        </>}
      </div>
    </main>
  </div>;
}

function Overview({ data, onInvestigate }: { data: Data; onInvestigate: () => void }) {
  const steps = ['Saw sensor data', 'Active-cut extraction', 'Engineered features', 'Random Forest', 'Risk score', 'Inspect / Continue'];
  return <>
    <div className="hero"><div><span className="eyebrow orange">THE INDUSTRIAL PROBLEM</span><h2>A part can pass Saw weight inspection and still fail downstream at Milling.</h2><p>The final system uses Saw active-cut signals to produce an inspection recommendation before Milling begins.</p><button className="primary-action" onClick={onInvestigate}><Search size={17} /> Investigate a Product</button></div><div className="hero-badge"><AlertTriangle size={18} /><strong>81</strong><span>later Milling failures</span></div></div>
    <p className="section-kicker">Dataset evidence, not model performance</p>
    <div className="kpis"><div className="kpi"><strong>99</strong><span>documented Saw misalignments</span><small>Recorded in the dataset</small></div><div className="kpi"><strong>100%</strong><span>passed Saw weight QC</span><small>Existing QC blind spot</small></div><div className="kpi"><strong>{data.later_milling_failures}</strong><span>later Milling failures</span><small>Observed downstream outcome</small></div></div>
    <div className="panel workflow-panel"><h3>How the final system works</h3><div className="workflow">{steps.map((step, index) => <div className="workflow-step" key={step}><span>0{index + 1}</span><strong>{step}</strong>{index < steps.length - 1 && <i>→</i>}</div>)}</div><div className="decision-rule"><span><b>Risk score &lt; 0.25</b> Continue</span><span><b>Risk score ≥ 0.25</b> Inspection recommended / Hold &amp; inspect</span></div></div>
  </>;
}

function Investigation({ products, productId, setProductId, product, investigate }: { products: Data[]; productId: string; setProductId: (value: string) => void; product: Data; investigate: (id?: string) => void }) {
  return <><div className="investigate-search"><div><span className="eyebrow orange">OPERATOR LOOKUP</span><h2>Investigate one part</h2><p className="lede">Inspect the final Random Forest result and the actual Saw process signals for a selected workpiece.</p></div><div className="search-control"><input value={productId} onChange={(event) => setProductId(event.target.value)} onKeyDown={(event) => event.key === 'Enter' && investigate()} list="product-ids" placeholder="Search or select Product ID" /><datalist id="product-ids">{products.map((item) => <option key={item.product_id} value={item.product_id} />)}</datalist><button onClick={() => investigate()}><Search size={17} /> Search</button></div></div>{!product ? <div className="empty-state"><Search size={22} /><strong>Select a product to investigate</strong><span>Search for a Product ID or choose a suggestion in the search field.</span></div> : <ProductDetail product={product} />}</>;
}

function ProductDetail({ product }: { product: Data }) {
  const flagged = Boolean(product.flagged);
  return <><div className="investigation-summary"><div><span className="eyebrow">PRODUCT</span><strong>{product.product_id}</strong><small>Saw operation · {product.duration_seconds}s active cut</small></div><div><span className="eyebrow">RISK SCORE</span><strong className="risk-number">{Number(product.risk_score).toFixed(2)}</strong><small>Threshold · 0.25</small></div><div className={flagged ? 'recommendation danger' : 'recommendation'}><strong>{flagged ? 'INSPECTION RECOMMENDED' : 'CONTINUE'}</strong><span>{flagged ? 'Above inspection threshold' : 'Below inspection threshold'}</span></div></div><div className="panel"><h3>Saw sensor signals</h3><p className="panel-note">Recorded physical signals during the active-cut operation. They are shown for process investigation, not as a direct explanation of the model decision.</p><div className="signal-grid">{product.signals?.map((signal: Data) => <div className="signal-card" key={signal.name}><strong>{signal.name}</strong><ResponsiveContainer width="100%" height={140}><LineChart data={signal.points}><XAxis dataKey="seconds" hide /><YAxis hide domain={['auto', 'auto']} /><Tooltip /><Line type="monotone" dataKey="value" stroke="var(--primary)" dot={false} strokeWidth={2} /></LineChart></ResponsiveContainer><small>{signal.signal}</small></div>)}</div></div><div className="panel historical-panel"><h3>Historical Outcome</h3><p className="panel-note">Recorded after the historical production run. This information was not available to the model before prediction.</p><div className="history"><span><b className="pass-text">✓</b> Saw Weight QC <strong>{product.saw_weight_pass ? 'PASS' : 'FAIL'}</strong></span><span><b className={product.milling_qc_pass ? 'pass-text' : 'fail-text'}>{product.milling_qc_pass ? '✓' : '!'}</b> Milling QC <strong>{product.milling_qc_known ? (product.milling_qc_pass ? 'PASS' : 'FAIL') : 'UNKNOWN'}</strong></span><span><b className={product.true_label ? 'fail-text' : 'pass-text'}>{product.true_label ? '!' : '✓'}</b> Target defect <strong>{product.true_label ? 'YES' : 'NO'}</strong></span></div></div></>;
}

function Performance({ features }: { features: Data[] }) {
  const metrics = [
    ['Precision', '95.2%', 'Of flagged parts, the share that were actual target defects.'],
    ['Recall', '66.7%', 'The share of target defects detected by the model.'],
    ['Accuracy', '85.3%', 'The share of benchmark parts classified correctly overall.'],
    ['False Positive Rate', '2.22%', 'The share of non-target parts incorrectly flagged for inspection.'],
    ['F1-Score', '78.4%', 'The harmonic mean of precision and recall.'],
  ];

  return <><p className="lede">Fixed benchmark results for the final Random Forest model on 75 products. The threshold was locked at 0.25.</p><div className="metric-grid performance-metrics">{metrics.map(([label, value, explanation]) => <div className="metric" key={label}><span>{label}</span><strong>{value}</strong><small>{explanation}</small></div>)}</div><div className="two-col"><div className="panel"><h3>Confusion Matrix</h3><div className="matrix"><div className="matrix-corner" /><div className="matrix-heading matrix-predicted-non-target">Predicted Non-Target</div><div className="matrix-heading matrix-predicted-inspect">Predicted Inspect</div><div className="matrix-heading matrix-actual-non-target">Actual Non-Target</div><div className="matrix-value matrix-true-negative"><b>44</b></div><div className="matrix-value alarm matrix-false-positive"><b>1</b></div><div className="matrix-heading matrix-actual-target">Actual Target Defect</div><div className="matrix-value miss matrix-false-negative"><b>10</b></div><div className="matrix-value matrix-true-positive"><b>20</b></div></div></div><div className="panel"><h3>Top Model Features</h3><p className="panel-note">Engineered statistical features used by the final Random Forest.</p><div className="importance-list">{features.map((feature) => <div key={feature.feature}><span>{feature.feature}</span><i><b style={{ width: `${Math.max(4, feature.importance * 100 / 0.14)}%` }} /></i><small>{(feature.importance * 100).toFixed(1)}%</small></div>)}</div></div></div></>;
}

createRoot(document.getElementById('root')!).render(<App />);

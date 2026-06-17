import React, { useState, useEffect, useMemo } from 'react';
import { LayoutDashboard, Activity, ShoppingCart, Calendar, ChevronDown, ChevronRight, FileCode2 } from 'lucide-react';
import { AgGridReact } from 'ag-grid-react';
import { ModuleRegistry, AllCommunityModule } from 'ag-grid-community';
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-quartz.css";
import VoucherViewer from './VoucherViewer';

// Register the AG Grid community features globally
ModuleRegistry.registerModules([AllCommunityModule]);

const formatCurrency = (val) => {
  if (val === undefined || val === null || val === 0 || val === '0') return '';
  const num = Number(val);
  if (isNaN(num) || num === 0) return '';
  return num.toFixed(2);
};

const DataTable = ({ title, data, totals, columns, loading, onDrillDown }) => {
  const colDefs = useMemo(() => {
    const stringColumns = ['Month', 'Invoice_Date', 'Invoice_No', 'Party_Name', 'GSTIN', 'Category', 'State_Code', 'Particular', 'Detail', '%', 'Item_Group'];
    return columns.map(col => {
      const isString = stringColumns.includes(col);
      
      let headerText = col.replace(/_/g, ' ');
      if (col === 'Amount1' || col === 'Amount2') headerText = 'Amount';
      if (col === 'Sl') headerText = 'Sl.';
      
      return {
        field: col,
        headerName: headerText,
        flex: 1,
        minWidth: 120,
        sortable: true,
        filter: true,
        cellStyle: isString || col === 'SNo' || col === 'Sl' || col === 'Particulars' || col === 'Remarks' ? { textAlign: 'left', fontWeight: col === 'Month' || col === 'Invoice_Date' || col === 'Particular' || col === 'Item_Group' ? 'bold' : 'normal' } : { textAlign: 'right', color: '#9ca3af' },
        valueFormatter: isString || col === 'SNo' || col === 'Sl' || col === 'Particulars' || col === 'Remarks' || col === 'Date' ? undefined : (params) => formatCurrency(params.value)
      };
    });
  }, [columns]);

  const defaultColDef = useMemo(() => {
    return {
      resizable: true,
    };
  }, []);

  const pinnedBottomRowData = useMemo(() => {
    if (!totals || Object.keys(totals).length === 0) return [];
    
    // Set the label depending on the report type
    let totalLabel = { Month: 'Grand Total' };
    if (title.includes('GSTR1') || title.includes('GSTR2')) totalLabel = { Invoice_Date: 'Grand Total' };
    if (title.includes('Item Groupwise')) totalLabel = { Item_Group: 'Grand Total' };
    
    return [{ ...totals, ...totalLabel }];
  }, [totals, title]);

  return (
    <div className="flex flex-col flex-1 overflow-hidden p-6 bg-[#0d1117]">
      <div className="flex items-center justify-between mb-6 shrink-0">
        <h2 className="text-2xl font-semibold text-white flex items-center gap-2">
          {title.includes('Sale') ? <Activity className="text-emerald-400" /> : <ShoppingCart className="text-blue-400" />}
          {title}
        </h2>
        <div className="text-sm text-gray-400">
          Powered by live double-entry FoxPro data
        </div>
      </div>

      <div className="flex-1 relative rounded-xl overflow-hidden shadow-2xl border border-gray-800 ag-theme-quartz-dark min-h-0" style={{ '--ag-background-color': '#111827', '--ag-header-background-color': '#030712' }}>
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
          </div>
        ) : (
          <div className="absolute inset-0">
            <AgGridReact
              rowData={data}
              columnDefs={colDefs}
              defaultColDef={defaultColDef}
              pinnedBottomRowData={pinnedBottomRowData}
              animateRows={true}
              rowSelection="multiple"
              theme="legacy"
              onRowDoubleClicked={(e) => onDrillDown && onDrillDown(e.data)}
            />
          </div>
        )}
      </div>
    </div>
  );
};

const MenuItem = ({ item, level = 0, onSelect, activeMenuId }) => {
  const [isOpen, setIsOpen] = useState(false);
  const hasChildren = item.children && item.children.length > 0;
  
  const isActive = activeMenuId === item.id;

  const handleClick = () => {
    if (hasChildren) {
      setIsOpen(!isOpen);
    } else {
      onSelect(item);
    }
  };

  return (
    <div className="w-full">
      <button 
        onClick={handleClick}
        style={{ paddingLeft: `${(level * 1) + 1}rem` }}
        className={`w-full flex items-center justify-between py-2 pr-4 text-sm transition-colors ${isActive ? 'bg-emerald-500/10 text-emerald-400 border-r-2 border-emerald-500' : 'text-gray-400 hover:bg-gray-800 hover:text-white'}`}
      >
        <span className="flex items-center gap-2 truncate">
          {!hasChildren && level > 0 && <span className="w-1 h-1 rounded-full bg-gray-600"></span>}
          <span className="truncate">{item.label}</span>
        </span>
        {hasChildren && (
          isOpen ? <ChevronDown className="w-4 h-4 opacity-50" /> : <ChevronRight className="w-4 h-4 opacity-50" />
        )}
      </button>
      
      {hasChildren && isOpen && (
        <div className="flex flex-col border-l border-gray-800 ml-4 mt-1">
          {item.children.map(child => (
            <MenuItem key={child.id} item={child} level={level + 1} onSelect={onSelect} activeMenuId={activeMenuId} />
          ))}
        </div>
      )}
    </div>
  );
};

export default function App() {
  const [menuTree, setMenuTree] = useState([]);
  const [activeMenu, setActiveMenu] = useState(null);
  
  const [startDate, setStartDate] = useState('2025-04-01');
  const [endDate, setEndDate] = useState('2026-03-31');
  
  const [data, setData] = useState([]);
  const [totals, setTotals] = useState({});
  const [loading, setLoading] = useState(false);
  
  const [drillPath, setDrillPath] = useState([]);
  const [drillData, setDrillData] = useState([]);
  const [drillDetails, setDrillDetails] = useState(null);
  
  // Reset drill down if menu or dates change
  useEffect(() => {
    setDrillPath([]);
    setDrillData([]);
    setDrillDetails(null);
  }, [activeMenu, startDate, endDate]);

  useEffect(() => {
    const fetchMenu = async () => {
      try {
        const res = await fetch('/api/menu');
        const json = await res.json();
        setMenuTree(json);
      } catch (e) {
        console.error("Failed to fetch menu", e);
      }
    };
    fetchMenu();
  }, []);

  useEffect(() => {
    if (!activeMenu || !startDate || !endDate) return;

    const label = activeMenu.label.toLowerCase();
    let isSales = label.includes('sale typewise');
    let isPurchases = label.includes('purchase typewise');
    let isGstr1 = label.includes('gstr1');
    let isGstr2 = label.includes('gstr2');
    let isGstr3b = label.includes('summary/gstr 3b');
    let isItemSale = label.includes('item groupwise sale');
    let isItemPurchase = label.includes('item groupwise purchase');
    let isVat24 = label.includes('vat 24');
    let isVatMonthly = label.includes('monthly/quaterly');
    let isVatSummary = label === 'summary';
    let isAnyVat = isVat24 || isVatMonthly || isVatSummary;
    
    // Stock Reports
    let isQtyWise = label.includes('qty wise');
    let isQtyVal = label.includes('qty+value');
    let isItemLedger = label.includes('item ledger');
    let isStockRegisterGroup = label === 'group' && activeMenu.id.includes('main'); // rough check
    let isStockRegisterItem = label === 'item' && activeMenu.id.includes('main'); 
    let isStockRegister = label.includes('stock register') || isStockRegisterGroup || isStockRegisterItem;
    let isSiteWise = label.includes('site wise');
    let isDiamond = label.includes('diamond summary');
    let isLooseTag = label.includes('loose/tag');
    let isComplete = label.includes('complete detailed');
    let isStockList = label.includes('stock list');
    let isPrint = label.includes('print');
    
    let isAnyStock = isQtyWise || isQtyVal || isItemLedger || isStockRegister || isSiteWise || isDiamond || isLooseTag || isComplete || isStockList || isPrint;
    
    if (isSales || isPurchases || isGstr1 || isGstr2 || isGstr3b || isItemSale || isItemPurchase || isAnyVat || isAnyStock) {
      const fetchData = async () => {
        setLoading(true);
        try {
          const endpoint = isVat24 ? '/api/vat24' :
                           isVatMonthly ? '/api/vat-monthly' :
                           isVatSummary ? '/api/vat-summary' :
                           isGstr1 ? '/api/gstr1' :
                           isGstr2 ? '/api/gstr2' :
                           isGstr3b ? '/api/gstr3b' :
                           isItemSale ? '/api/item-group-register?type=sale' :
                           isItemPurchase ? '/api/item-group-register?type=purchase' :
                           isQtyWise ? '/api/stock-qty-wise' :
                           isQtyVal ? '/api/stock-qty-value' :
                           isItemLedger ? '/api/item-ledger' :
                           isStockRegister && isStockRegisterGroup ? '/api/stock-register?group_by=group' :
                           isStockRegister ? '/api/stock-register?group_by=item' :
                           isSiteWise ? '/api/stock-site-wise' :
                           isLooseTag ? '/api/stock-loose-tag' :
                           isDiamond ? '/api/stock-diamond-summary' :
                           isComplete ? '/api/stock-complete-detailed' :
                           isStockList ? '/api/stock-list' :
                           isPrint ? '/api/stock-register-print' :
                           isSales ? '/api/sale-register' : 
                           '/api/purchase-register';
                           
          const separator = endpoint.includes('?') ? '&' : '?';
          const url = `${endpoint}${separator}start_date=${startDate}&end_date=${endDate}`;
          const res = await fetch(url);
          const json = await res.json();
          
          if (isGstr3b) {
             setData(Array.isArray(json) ? json : []);
             setTotals(null);
          } else if (isItemSale || isItemPurchase) {
             setData(Array.isArray(json) ? json : []);
             const tPieces = Array.isArray(json) ? json.reduce((sum, row) => sum + (Number(row.Pieces) || 0), 0) : 0;
             const tGross = Array.isArray(json) ? json.reduce((sum, row) => sum + (Number(row.Gross_Wt) || 0), 0) : 0;
             const tNet = Array.isArray(json) ? json.reduce((sum, row) => sum + (Number(row.Net_Wt) || 0), 0) : 0;
             const tFine = Array.isArray(json) ? json.reduce((sum, row) => sum + (Number(row.Fine_Wt) || 0), 0) : 0;
             const tLabor = Array.isArray(json) ? json.reduce((sum, row) => sum + (Number(row.Labor_Amt) || 0), 0) : 0;
             const tStone = Array.isArray(json) ? json.reduce((sum, row) => sum + (Number(row.Stone_Amt) || 0), 0) : 0;
             const tAmount = Array.isArray(json) ? json.reduce((sum, row) => sum + (Number(row.Amount) || 0), 0) : 0;
             
             setTotals({
                 Item_Group: 'Grand Total',
                 Pieces: tPieces,
                 Gross_Wt: tGross,
                 Net_Wt: tNet,
                 Fine_Wt: tFine,
                 Labor_Amt: tLabor,
                 Stone_Amt: tStone,
                 Amount: tAmount
             });
          } else if (isGstr1 || isGstr2) {
             setData(Array.isArray(json) ? json : []);
             const tTaxable = Array.isArray(json) ? json.reduce((sum, row) => sum + (Number(row.Taxable_Value) || 0), 0) : 0;
             const tCGST = Array.isArray(json) ? json.reduce((sum, row) => sum + (Number(row.CGST) || 0), 0) : 0;
             const tSGST = Array.isArray(json) ? json.reduce((sum, row) => sum + (Number(row.SGST) || 0), 0) : 0;
             const tIGST = Array.isArray(json) ? json.reduce((sum, row) => sum + (Number(row.IGST) || 0), 0) : 0;
             const tTotal = Array.isArray(json) ? json.reduce((sum, row) => sum + (Number(row.Total_Value) || 0), 0) : 0;
             
             setTotals({
                 Invoice_Date: 'Grand Total',
                 Taxable_Value: tTaxable,
                 CGST: tCGST,
                 SGST: tSGST,
                 IGST: tIGST,
                 Total_Value: tTotal
             });
          } else if (isAnyVat) {
             setData(Array.isArray(json) ? json : []);
             const tTaxable = Array.isArray(json) ? json.reduce((sum, row) => sum + (Number(row.Taxable_Value) || 0), 0) : 0;
             const tVatAmt = Array.isArray(json) ? json.reduce((sum, row) => sum + (Number(row.VAT_Amount) || 0), 0) : 0;
             const tTotal = Array.isArray(json) ? json.reduce((sum, row) => sum + (Number(row.Total_Value) || 0), 0) : 0;
             
             let totalLabel = {};
             if (isVat24 || isVatSummary || isAnyStock) {
                 setData(Array.isArray(json) ? json : []);
                 setTotals(null);
             } else {
                 if (isVatMonthly) totalLabel = { Month: 'Grand Total' };
                 
                 setTotals({
                     ...totalLabel,
                     Taxable_Value: tTaxable,
                     VAT_Amount: tVatAmt,
                     Total_Value: tTotal
                 });
             }
          } else {
             if (json.data) {
               setData(json.data);
               setTotals(json.totals);
             } else if (json.text_report) {
               setData([{ raw_text: json.text_report }]);
               setTotals(null);
             } else {
               setData(Array.isArray(json) ? json : []);
               setTotals(null);
             }
          }
        } catch (e) {
          console.error("Error fetching data:", e);
          setData([]);
          setTotals({});
        }
        setLoading(false);
      };
      fetchData();
    }
  }, [activeMenu, startDate, endDate]);

  const salesColumns = ['Month', 'Retail Sale', 'Tax Invoice', 'Total', 'SGST', 'CGST', 'Central Sale', 'Others', 'IGST', 'Total Sale', 'Net Amount'];
  const purchaseColumns = ['Month', 'URD Purchase', 'Tax Invoice', 'Total', 'SGST', 'CGST', 'CST Purchase', 'Others', 'IGST', 'Total Purchase', 'Net Amount'];
  const gstrColumns = ['Invoice_Date', 'Invoice_No', 'Party_Name', 'GSTIN', 'Category', 'State_Code', 'Taxable_Value', 'CGST', 'SGST', 'IGST', 'Total_Value'];
  const gstr3bColumns = ['Particular', 'Detail', '%', 'Weight', 'Amount', 'IGST OUT', 'CGST OUT', 'SGST OUT', 'IGST IN', 'CGST IN', 'SGST IN', 'Total', 'GST ADJ.'];
  const itemGroupColumns = ['Item_Group', 'Pieces', 'Gross_Wt', 'Net_Wt', 'Fine_Wt', 'Labor_Amt', 'Stone_Amt', 'Amount'];
  const vat24Columns = ['SNo', 'Sl', 'Particulars', 'Remarks', 'Amount1', 'Amount2', 'Date'];
  const vatMonthlyColumns = ['Month', 'Taxable_Value', 'VAT_Amount', 'Total_Value'];
  const vatSummaryColumns = ['Series', 'Item_Name', 'Weight', 'Amount', 'Ptax', 'Tax', 'Surcharge'];

  // Stock Summary Columns
  const stockQtyWiseColumns = ['Item_Name', 'Site', 'Stamp_Batch', 'Op_Wt', 'Op_Amt', 'Rec_Wt', 'Rec_Amt', 'Iss_Wt', 'Iss_Amt', 'Cl_Wt', 'Cl_Amt'];
  const stockQtyValColumns = ['Item_Name', 'Op_Wt', 'Op_Val', 'Rec_Wt', 'Rec_Val', 'Iss_Wt', 'Iss_Val', 'Cl_Wt', 'Cl_Val'];
  const stockRegisterColumns = ['Name', 'Opening', 'Inward', 'Outward', 'Closing'];
  const stockSiteWiseColumns = ['Item_Name', 'Stamp_Batch', 'Op_Pcs', 'Op_Wt', 'Pur_Pcs', 'Pur_Wt', 'Rec_Pcs', 'Rec_Wt', 'Sale_Pcs', 'Sale_Wt', 'Iss_Pcs', 'Iss_Wt', 'Cl_Pcs', 'Cl_Wt'];
  const itemLedgerColumns = ['Date', 'Voucher_No', 'Item_Name', 'Particulars', 'Inward_Wt', 'Outward_Wt'];
  const diamondSummaryColumns = ['Diamond_Item', 'Pieces', 'Carat_Wt'];
  const looseTagColumns = ['Item_Name', 'Tag_Wt', 'Loose_Wt', 'Total_Wt'];
  const completeDetailedColumns = ['Site', 'Item_Name', 'Opening', 'Inward', 'Outward', 'Closing', 'Value'];
  const stockListColumns = ['Item_Name', 'Closing_Pcs', 'Closing_Wt'];

  const renderContent = () => {

    if (!activeMenu) {
      return (
        <div className="flex-1 flex items-center justify-center text-gray-500">
          Select a report from the sidebar to view data
        </div>
      );
    }

    if (drillPath.length === 2 && drillDetails) {
       return <VoucherViewer details={drillDetails} onBack={() => {
          setDrillPath(prev => prev.slice(0, 1));
          setDrillDetails(null);
       }} />;
    }

    if (drillPath.length === 1) {
       const isItemGroup = !!drillPath[0].itemGroup;
       const title = isItemGroup 
           ? `Item Register - ${drillPath[0].itemGroup}` 
           : `Register Details - ${drillPath[0].month} ${startDate.split('-')[0]}`;
           
       const cols = isItemGroup
           ? ['Date', 'Type', 'Vou_No', 'Party_Name', 'Item_Name', 'Purity', 'Tag_No', 'Pc', 'Gr_Wt', 'Less_Wt', 'Net_Wt', 'Taxable_Amt']
           : ['Date', 'Vou.No.', 'Party_Name', 'State', 'GSTIN', 'Narration', 'Amount', 'SGST', 'CGST', 'IGST', 'Bill_Amount'];

       return <DataTable 
         title={title} 
         data={drillData} 
         columns={cols} 
         loading={loading}
         onDrillDown={async (row) => {
            if (row && row.TRNID) {
               setDrillPath(prev => [...prev, { trnid: row.TRNID }]);
               setLoading(true);
               try {
                  const res = await fetch(`/api/voucher-details?trn_id=${row.TRNID}`);
                  const json = await res.json();
                  setDrillDetails(json);
               } catch(e) { console.error(e); }
               setLoading(false);
            }
         }}
       />;
    }

    const label = activeMenu.label.toLowerCase();
    
    // Unified drill-down handler for all reports
    const handleDrillDown = async (row) => {
       if (!row) return;
       
       if (row.TRNID) {
          // Direct jump to voucher (e.g. from GSTR1, VAT24, etc.)
          setDrillPath([{ trnid: row.TRNID }, { trnid: row.TRNID }]); // push to level 2
          setLoading(true);
          try {
             const res = await fetch(`/api/voucher-details?trn_id=${row.TRNID}`);
             const json = await res.json();
             setDrillDetails(json);
          } catch(e) { console.error(e); }
          setLoading(false);
       } else if (row.Month && row.Month !== 'Total' && row.Month !== 'Grand Total') {
          // Drill down to register
          let vtype = label.includes('sale') ? 'SALE' : 'PURCHASE';
          setDrillPath([{ month: row.Month }]);
          setLoading(true);
          try {
             let year = parseInt(startDate.split('-')[0]);
             const url = `/api/register-details?start_date=${startDate}&end_date=${endDate}&month=${row.Month}&year=${year}&vtype=${vtype}`;
             const res = await fetch(url);
             const json = await res.json();
             setDrillData(json);
          } catch(e) { console.error(e); }
          setLoading(false);
       } else if (row.Item_Group && row.Item_Group !== 'Grand Total') {
          // Drill down to item register
          let vtype = label.includes('sale') ? 'SALE' : 'PURCHASE';
          setDrillPath([{ itemGroup: row.Item_Group }]);
          setLoading(true);
          try {
             const url = `/api/item-register?start_date=${startDate}&end_date=${endDate}&vtype=${vtype}&item_group=${encodeURIComponent(row.Item_Group)}`;
             const res = await fetch(url);
             const json = await res.json();
             setDrillData(json);
          } catch(e) { console.error(e); }
          setLoading(false);
       }
    };
    
    if (label.includes('item groupwise sale')) {
      return <DataTable title="Item Groupwise Sale" data={data} totals={totals} columns={itemGroupColumns} loading={loading} onDrillDown={handleDrillDown} />;
    } else if (label.includes('item groupwise purchase')) {
      return <DataTable title="Item Groupwise Purchase" data={data} totals={totals} columns={itemGroupColumns} loading={loading} onDrillDown={handleDrillDown} />;
    } else if (label.includes('sale typewise')) {
      return <DataTable title="Sale Tax Register" data={data} totals={totals} columns={salesColumns} loading={loading} onDrillDown={handleDrillDown} />;
    } else if (label.includes('purchase typewise')) {
      return <DataTable title="Purchase Tax Register" data={data} totals={totals} columns={purchaseColumns} loading={loading} onDrillDown={handleDrillDown} />;
    } else if (label.includes('gstr1')) {
      return <DataTable title="GSTR1 Register" data={data} totals={totals} columns={gstrColumns} loading={loading} onDrillDown={handleDrillDown} />;
    } else if (label.includes('gstr2')) {
      return <DataTable title="GSTR2 Register" data={data} totals={totals} columns={gstrColumns} loading={loading} onDrillDown={handleDrillDown} />;
    } else if (label.includes('summary/gstr 3b')) {
      return <DataTable title="GSTR 3B Summary" data={data} totals={totals} columns={gstr3bColumns} loading={loading} onDrillDown={handleDrillDown} />;
    } else if (label.includes('vat 24')) {
      return <DataTable title="VAT 24 Register" data={data} totals={totals} columns={vat24Columns} loading={loading} onDrillDown={handleDrillDown} />;
    } else if (label.includes('monthly/quaterly')) {
      return <DataTable title="VAT Monthly/Quarterly Report" data={data} totals={totals} columns={vatMonthlyColumns} loading={loading} onDrillDown={handleDrillDown} />;
    } else if (label === 'summary') {
      return <DataTable title="VAT Summary" data={data} totals={totals} columns={vatSummaryColumns} loading={loading} onDrillDown={handleDrillDown} />;
    } else if (label.includes('print') && data.length > 0 && data[0].raw_text) {
      return (
        <div className="flex-1 overflow-auto bg-black text-green-400 p-8 font-mono text-sm leading-relaxed whitespace-pre-wrap">
          {data[0].raw_text}
        </div>
      );
    } else if (label.includes('qty wise')) {
      return <DataTable title="Stock - Qty Wise" data={data} totals={totals} columns={stockQtyWiseColumns} loading={loading} onDrillDown={handleDrillDown} />;
    } else if (label.includes('qty+value')) {
      return <DataTable title="Stock - Qty+Value" data={data} totals={totals} columns={stockQtyValColumns} loading={loading} onDrillDown={handleDrillDown} />;
    } else if (label.includes('item ledger')) {
      return <DataTable title="Item Ledger" data={data} totals={totals} columns={itemLedgerColumns} loading={loading} onDrillDown={handleDrillDown} />;
    } else if (label === 'group' || label === 'item' || label.includes('stock register')) {
      return <DataTable title={`Stock Register - ${activeMenu.label}`} data={data} totals={totals} columns={stockRegisterColumns} loading={loading} onDrillDown={handleDrillDown} />;
    } else if (label.includes('site wise')) {
      return <DataTable title="Stock - Site Wise" data={data} totals={totals} columns={stockSiteWiseColumns} loading={loading} onDrillDown={handleDrillDown} />;
    } else if (label.includes('loose/tag')) {
      return <DataTable title="Stock - Loose/Tag Wise" data={data} totals={totals} columns={looseTagColumns} loading={loading} onDrillDown={handleDrillDown} />;
    } else if (label.includes('diamond summary')) {
      return <DataTable title="Diamond Summary" data={data} totals={totals} columns={diamondSummaryColumns} loading={loading} onDrillDown={handleDrillDown} />;
    } else if (label.includes('complete detailed')) {
      return <DataTable title="Complete Detailed Stock" data={data} totals={totals} columns={completeDetailedColumns} loading={loading} onDrillDown={handleDrillDown} />;
    } else if (label.includes('stock list')) {
      return <DataTable title="Stock List" data={data} totals={totals} columns={stockListColumns} loading={loading} onDrillDown={handleDrillDown} />;
    } else {
      return (
        <div className="flex-1 flex flex-col items-center justify-center p-8 bg-[#0d1117]">
          <div className="bg-gray-900 border border-gray-800 p-8 rounded-2xl max-w-lg w-full text-center shadow-2xl">
            <FileCode2 className="w-16 h-16 text-emerald-500 mx-auto mb-6" />
            <h2 className="text-2xl font-bold text-white mb-2">{activeMenu.label}</h2>
            <div className="inline-block bg-yellow-500/10 text-yellow-500 text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-full mb-6">
              Under Construction
            </div>
            <p className="text-gray-400 mb-6">
              This FoxPro module has not yet been migrated to the new Web Engine. The original FoxPro command for this module is:
            </p>
            <div className="bg-black/50 p-4 rounded-lg font-mono text-sm text-emerald-400 break-all border border-gray-800">
              {activeMenu.cmd || 'NO COMMAND SPECIFIED'}
            </div>
          </div>
        </div>
      );
    }
  };

  return (
    <div className="flex h-screen bg-[#0d1117] text-gray-200 font-sans">
      
      {/* Sidebar */}
      <div className="w-72 bg-gray-950 border-r border-gray-800 flex flex-col z-20 shadow-xl">
        <div className="p-6 border-b border-gray-800 flex items-center gap-3 shrink-0">
          <div className="bg-emerald-500/20 p-2 rounded-lg border border-emerald-500/30">
            <LayoutDashboard className="w-6 h-6 text-emerald-400" />
          </div>
          <span className="font-bold text-xl tracking-wide text-white">FoxPro <span className="font-light text-gray-400">Hub</span></span>
        </div>
        
        <div className="flex-1 overflow-y-auto py-4 custom-scrollbar">
          {menuTree.length === 0 ? (
            <div className="flex items-center justify-center h-20">
               <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-emerald-500"></div>
            </div>
          ) : (
            menuTree.map(item => (
              <MenuItem 
                key={item.id} 
                item={item} 
                onSelect={(menu) => setActiveMenu(menu)} 
                activeMenuId={activeMenu?.id}
              />
            ))
          )}
        </div>
        
        <div className="p-6 border-t border-gray-800 bg-gray-950/80 shrink-0">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">Global Filter</div>
          <div className="space-y-4">
            <div>
              <label className="text-xs text-gray-400 mb-1 flex items-center gap-1"><Calendar className="w-3 h-3"/> Start Date</label>
              <input 
                type="date" 
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all"
              />
            </div>
            <div>
              <label className="text-xs text-gray-400 mb-1 flex items-center gap-1"><Calendar className="w-3 h-3"/> End Date</label>
              <input 
                type="date" 
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {renderContent()}
      </div>
      
    </div>
  );
}

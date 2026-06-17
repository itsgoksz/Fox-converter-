import React from 'react';
import { FileText, ArrowLeft } from 'lucide-react';

const formatCurrency = (val) => {
  if (val === undefined || val === null || val === 0 || val === '0') return '';
  const num = Number(val);
  if (isNaN(num) || num === 0) return '';
  return num.toFixed(3);
};

const formatAmt = (val) => {
  if (val === undefined || val === null || val === 0 || val === '0') return '';
  const num = Number(val);
  if (isNaN(num) || num === 0) return '';
  return num.toFixed(2);
};

export default function VoucherViewer({ details, onBack }) {
  if (!details || !details.header) {
    return (
      <div className="flex flex-col flex-1 items-center justify-center bg-[#0d1117] text-white">
         <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500 mb-4"></div>
         <div>Loading Voucher Details...</div>
      </div>
    );
  }

  const h = details.header;
  const items = details.items || [];

  // Derived calculations
  const totalWeight = items.reduce((acc, it) => acc + (Number(it.Weight) || 0), 0);
  const totalNetWt = items.reduce((acc, it) => acc + (Number(it.Net_Wt) || 0), 0);
  
  // Tax Total
  const taxTotal = (h.SGST || 0) + (h.CGST || 0) + (h.IGST || 0);
  const netBal = (h.Total_Sale || 0) + taxTotal;

  return (
    <div className="flex flex-col flex-1 p-6 bg-[#0d1117] overflow-hidden">
      {/* Top Navigation */}
      <div className="flex items-center gap-4 mb-4">
        <button 
          onClick={onBack}
          className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Register
        </button>
        <h2 className="text-xl font-bold text-emerald-400 flex items-center gap-2">
          <FileText className="w-5 h-5" />
          Voucher Details (Vou.No: {h.Vou_No})
        </h2>
      </div>

      {/* Main FoxPro-style Container */}
      <div className="flex-1 overflow-y-auto bg-[#c6ffc6] rounded shadow-2xl border border-gray-400 flex flex-col min-h-0 text-black font-sans text-xs p-1" style={{ fontFamily: 'Arial, sans-serif' }}>
        
        {/* Top Header Section */}
        <div className="flex gap-2 border-b border-gray-400 pb-1 shrink-0 bg-[#d9ebd9]">
          
          {/* Left Top Block */}
          <div className="flex-1 grid grid-cols-[100px_1fr] gap-x-2 gap-y-1 p-1">
             <div className="text-red-700">Account</div>
             <div className="font-bold bg-white px-1 border border-gray-300 shadow-inner">{h.Party_Name}</div>
             
             <div className="text-red-700">Cash A/c</div>
             <div className="bg-white px-1 border border-gray-300 shadow-inner"></div>
             
             <div className="text-red-700">Narration</div>
             <div className="bg-white px-1 border border-gray-300 shadow-inner text-blue-900">{h.Narration}</div>
          </div>
          
          {/* Middle Top Block - Address box */}
          <div className="w-[300px] bg-black text-white font-mono text-[10px] p-1 overflow-hidden leading-tight font-bold">
             {h.Address}<br/>
             CUSTOMER GSTIN: {h.GSTIN}
          </div>

          {/* Right Top Block */}
          <div className="w-[350px] grid grid-cols-[80px_1fr_60px_1fr] gap-x-2 gap-y-1 p-1 items-center">
             <div className="text-blue-800">Series</div>
             <div className="font-bold bg-white px-1 border border-gray-300 shadow-inner">{h.Series}</div>
             <div className="text-blue-800 flex justify-end">T</div>
             <div className="bg-[#b3ffb3] px-1 border border-gray-300 shadow-inner"></div>

             <div className="text-blue-800">Date</div>
             <div className="font-bold text-black bg-white px-1 border border-gray-300 shadow-inner">{h.Date}</div>
             <div className="text-blue-800">Inv No.</div>
             <div className="bg-white px-1 border border-gray-300 shadow-inner"></div>
             
             <div className="text-blue-800">Bill No</div>
             <div className="font-bold bg-white px-1 border border-gray-300 shadow-inner">{h.Bill_No || h.Vou_No}</div>
             <div className="text-blue-800">Inv.Date</div>
             <div className="bg-white px-1 border border-gray-300 shadow-inner text-center">/ /</div>
          </div>
        </div>

        {/* Items Grid */}
        <div className="flex-1 overflow-auto mt-1 bg-white border border-gray-400">
          <table className="w-full text-xs text-left border-collapse whitespace-nowrap">
            <thead className="bg-[#e2e8f0] sticky top-0 z-10">
              <tr>
                {['Type', 'Tag.No.', 'Design', 'Item Name', 'Stamp', 'Remarks', 'Unit', 'Pc', 'Weight', 'Less', 'Net.Wt.', 'Add.Wt.', 'Tunch', 'Fine', 'Rate', 'Dia.Wt.', 'Stn.Wt.', 'Lbr', 'On', 'Dis.', 'Amount'].map(col => (
                  <th key={col} className="px-1 py-0.5 border-r border-b border-gray-400 font-bold bg-[#f0f0f0] shadow-sm">{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {items.map((it, idx) => (
                <tr key={idx} className="border-b border-gray-300 hover:bg-yellow-100">
                  <td className="px-1 border-r border-gray-300 bg-[#7ba9e3] text-white font-bold text-center">{it.Type}</td>
                  <td className="px-1 border-r border-gray-300">{it.Tag_No}</td>
                  <td className="px-1 border-r border-gray-300">{it.Design}</td>
                  <td className="px-1 border-r border-gray-300 font-bold">{it.Item_Name}</td>
                  <td className="px-1 border-r border-gray-300 text-center">{it.Stamp}</td>
                  <td className="px-1 border-r border-gray-300">{it.Remarks}</td>
                  <td className="px-1 border-r border-gray-300 text-center">{it.Unit}</td>
                  <td className="px-1 border-r border-gray-300 text-right">{formatCurrency(it.Pc)}</td>
                  <td className="px-1 border-r border-gray-300 text-right font-bold">{formatCurrency(it.Weight)}</td>
                  <td className="px-1 border-r border-gray-300 text-right">{formatCurrency(it.Less)}</td>
                  <td className="px-1 border-r border-gray-300 text-right font-bold">{formatCurrency(it.Net_Wt)}</td>
                  <td className="px-1 border-r border-gray-300 text-right">{formatCurrency(it.Add_Wt)}</td>
                  <td className="px-1 border-r border-gray-300 text-right font-bold">{formatCurrency(it.Tunch)}</td>
                  <td className="px-1 border-r border-gray-300 text-right font-bold">{formatCurrency(it.Fine)}</td>
                  <td className="px-1 border-r border-gray-300 text-right">{formatAmt(it.Rate)}</td>
                  <td className="px-1 border-r border-gray-300 text-right">{formatCurrency(it.Dia_Wt)}</td>
                  <td className="px-1 border-r border-gray-300 text-right">{formatCurrency(it.Stn_Wt)}</td>
                  <td className="px-1 border-r border-gray-300 text-right">{formatAmt(it.Lbr)}</td>
                  <td className="px-1 border-r border-gray-300 text-center">{it.On || 'Pc'}</td>
                  <td className="px-1 border-r border-gray-300 text-right">{it.Dis}</td>
                  <td className="px-1 text-right font-bold">{formatAmt(it.Amount)}</td>
                </tr>
              ))}
              {/* Fill remaining empty rows for authentic look */}
              {Array.from({ length: Math.max(0, 15 - items.length) }).map((_, idx) => (
                 <tr key={`empty-${idx}`} className="border-b border-gray-300">
                    {Array.from({ length: 21 }).map((_, cidx) => (
                       <td key={cidx} className="px-1 py-2 border-r border-gray-300"></td>
                    ))}
                 </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Bottom Totals Section */}
        <div className="flex mt-1 border-t-2 border-gray-400 shrink-0 gap-2 p-1">
          
          {/* Bottom Left Grid (Item Subtotals) */}
          <div className="w-[400px] grid grid-cols-[80px_60px_80px_60px] gap-x-1 gap-y-1 bg-[#d9ebd9] p-1 border border-gray-300">
             <div className="text-red-800">Dia.Val.</div>
             <div className="font-bold bg-[#b2ccff] px-1 text-right border border-gray-300">{h.Dia_Val ? formatAmt(h.Dia_Val) : ''}</div>
             <div className="text-red-800">Stn.Val.</div>
             <div className="bg-[#b2ccff] px-1 border border-gray-300"></div>

             <div className="text-red-800">Labour</div>
             <div className="font-bold bg-[#b2ccff] px-1 text-right border border-gray-300">{h.Labour_Val ? formatAmt(h.Labour_Val) : ''}</div>
             <div className="text-red-800">M.R.P.</div>
             <div className="bg-[#b2ccff] px-1 border border-gray-300"></div>

             <div className="text-red-800">T-M/Val.</div>
             <div className="bg-[#b2ccff] px-1 border border-gray-300"></div>
             <div className="text-red-800">T-D/Val.</div>
             <div className="font-bold bg-[#b2ccff] px-1 text-right border border-gray-300">{h.Dia_Val ? formatAmt(h.Dia_Val) : ''}</div>

             <div className="text-red-800">Design</div>
             <div className="bg-[#b2ccff] px-1 border border-gray-300"></div>
             <div className="text-red-800">Clarity</div>
             <div className="bg-[#b2ccff] px-1 border border-gray-300"></div>
             
             {/* Columns 5 & 6 offset */}
             <div className="col-start-1 col-span-2 grid grid-cols-2 mt-1">
                 <div className="text-red-800">Metal</div>
                 <div className="bg-[#b2ccff] px-1 border border-gray-300"></div>
                 <div className="text-red-800">T-Lbr.</div>
                 <div className="font-bold bg-[#b2ccff] px-1 text-right border border-gray-300">{h.Labour_Val ? formatAmt(h.Labour_Val) : ''}</div>
             </div>
             <div className="col-start-3 col-span-2 grid grid-cols-[1fr_40px] mt-1 gap-x-1">
                 <div className="flex gap-1 justify-end items-center"><span className="text-blue-900">No.</span> <span className="font-bold bg-[#b2ccff] w-10 text-center border border-gray-300">1</span></div>
                 <div className="flex gap-1 justify-end items-center"><span className="text-blue-900">Rows</span> <span className="font-bold bg-[#b2ccff] w-10 text-center border border-gray-300">{items.length}</span></div>
             </div>
          </div>

          {/* Middle Placeholder Box */}
          <div className="flex-1 bg-[#bcf5bc] border border-gray-300 p-1 flex items-start text-xs font-mono text-gray-700">
             {/* Intentionally left sparse to match the FoxPro empty space with green bg */}
          </div>

          {/* Bottom Right Grid (Invoice Totals) */}
          <div className="w-[450px] flex flex-col gap-1">
             
             {/* Total Sale Sub-grid */}
             <table className="w-full text-xs text-left border-collapse whitespace-nowrap bg-white border border-gray-400">
                <tbody>
                   <tr>
                      <td className="px-1 border-r border-b border-gray-300 text-red-800 w-[100px]">Total Sale</td>
                      <td className="px-1 border-r border-b border-gray-300 bg-[#b2ccff] text-right font-bold">{formatCurrency(totalWeight)}</td>
                      <td className="px-1 border-r border-b border-gray-300 bg-[#b2ccff] text-right font-bold">{formatCurrency(totalNetWt)}</td>
                      <td className="px-1 border-b border-gray-300 bg-[#b2ccff] text-right font-bold">{formatAmt(h.Total_Sale)}</td>
                   </tr>
                   <tr>
                      <td className="px-1 border-r border-gray-300 text-red-800">Return</td>
                      <td className="px-1 border-r border-gray-300 bg-[#b2ccff]"></td>
                      <td className="px-1 border-r border-gray-300 bg-[#b2ccff]"></td>
                      <td className="px-1 border-gray-300 bg-[#b2ccff]"></td>
                   </tr>
                </tbody>
             </table>

             {/* GST / Net Balance Block */}
             <div className="grid grid-cols-[100px_80px_1fr] gap-x-1 gap-y-[2px] items-center text-xs mt-1 font-bold">
                 <div className="text-blue-900 italic">Last Bal.</div>
                 <div className="col-span-2 bg-[#b2ccff] border border-gray-300 h-[18px]"></div>
                 
                 <div className="text-black">SGST/CGST</div>
                 <div className="bg-white border border-gray-300 px-1 text-right">3.000</div>
                 <div className="bg-white border border-gray-300 px-1 text-right">{formatAmt(taxTotal)}</div>
                 
                 {/* Middle lines (adjustments, roundoff, receipts) omitted for brevity to focus on net balance */}
                 <div className="col-span-3 h-1"></div>
                 
                 <div className="text-red-700 mt-2">SGST</div>
                 <div className="bg-white border border-gray-300 px-1 text-right mt-2">{formatAmt(h.SGST)}</div>
                 <div className="col-start-3 text-red-600 pl-4 mt-2">Adjustments</div>
                 
                 <div className="text-red-700">CGST</div>
                 <div className="bg-white border border-gray-300 px-1 text-right">{formatAmt(h.CGST)}</div>
                 <div className="col-start-3 text-green-700 pl-4 text-sm font-bold">Net Balance</div>
                 
                 <div className="col-span-3 grid grid-cols-3 gap-1 mt-1">
                    <div className="bg-white border border-gray-300 text-center text-green-600">Nil</div>
                    <div className="bg-white border border-gray-300 text-center text-green-600">Nil</div>
                    <div className="bg-white border border-gray-400 text-right font-bold text-base px-1 shadow-sm">{formatAmt(netBal)}</div>
                 </div>
             </div>
          </div>
        </div>
        
        {/* Footer Buttons Bar */}
        <div className="flex gap-1 mt-1 p-1 bg-[#d9ebd9] border-t border-gray-400 justify-center text-[10px] font-bold">
           {['Adjust', 'App.Return', 'Q.Save', 'Save', 'Cancel', 'Ledger', 'Delete', 'New', 'Print', 'Prev.', 'Next', 'Export', 'Import'].map(btn => (
             <button key={btn} className="bg-white border border-gray-400 px-2 py-0.5 hover:bg-gray-100 shadow-sm">{btn}</button>
           ))}
        </div>
      </div>
    </div>
  );
}

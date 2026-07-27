import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon, ExternalLink, Trophy } from 'lucide-react';

const PLATFORM_COLOR = {
  codeforces: "bg-cyan-500/10 text-cyan-400 border-cyan-500/30",
  leetcode: "bg-amber-500/10 text-amber-400 border-amber-500/30",
};

export default function ContestCalendar({ contests = [] }) {
  const [currentDate, setCurrentDate] = useState(new Date());

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];

  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const firstDayIndex = new Date(year, month, 1).getDay();

  const prevMonth = () => setCurrentDate(new Date(year, month - 1, 1));
  const nextMonth = () => setCurrentDate(new Date(year, month + 1, 1));

  // Map contests by day of month
  const contestsByDay = {};
  contests.forEach((c) => {
    const d = new Date(c.start_time);
    if (d.getFullYear() === year && d.getMonth() === month) {
      const dayNum = d.getDate();
      if (!contestsByDay[dayNum]) contestsByDay[dayNum] = [];
      contestsByDay[dayNum].push(c);
    }
  });

  const dayHeaders = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  return (
    <div className="saas-card p-6 space-y-6 border-cyan-500/20">
      {/* Calendar Top Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-xl font-bold text-white font-heading flex items-center gap-2">
            <CalendarIcon className="text-cyan-400" size={22} /> CP31 Competitive Contest Schedule
          </h2>
          <p className="text-xs text-slate-400">Monthly contest grid for Codeforces & LeetCode</p>
        </div>

        <div className="flex items-center gap-3">
          <button onClick={prevMonth} className="btn-secondary px-2.5 py-1.5 text-xs">
            <ChevronLeft size={16} />
          </button>
          <span className="font-mono text-sm font-bold text-white min-w-[140px] text-center">
            {monthNames[month]} {year}
          </span>
          <button onClick={nextMonth} className="btn-secondary px-2.5 py-1.5 text-xs">
            <ChevronRight size={16} />
          </button>
        </div>
      </div>

      {/* 7-Column Day Header */}
      <div className="grid grid-cols-7 gap-2 text-center text-xs font-bold text-slate-400 uppercase tracking-wider">
        {dayHeaders.map((dh) => (
          <div key={dh} className="py-1 bg-slate-950/60 rounded-lg border border-slate-800/60">
            {dh}
          </div>
        ))}
      </div>

      {/* Grid of Days */}
      <div className="grid grid-cols-7 gap-2">
        {/* Blank cells for offset */}
        {Array.from({ length: firstDayIndex }).map((_, i) => (
          <div key={`empty-${i}`} className="min-h-[100px] p-2 bg-slate-950/30 rounded-xl border border-slate-900 opacity-40" />
        ))}

        {/* Days of the month */}
        {Array.from({ length: daysInMonth }).map((_, i) => {
          const dayNum = i + 1;
          const dayContests = contestsByDay[dayNum] || [];
          const isToday = new Date().getDate() === dayNum && new Date().getMonth() === month && new Date().getFullYear() === year;

          return (
            <div
              key={dayNum}
              className={`min-h-[100px] p-2.5 rounded-xl border transition flex flex-col justify-start ${
                isToday
                  ? "bg-slate-900 border-cyan-500/50 shadow-md shadow-cyan-500/10"
                  : "bg-slate-950/80 border-slate-800/80 hover:border-slate-700"
              }`}
            >
              <div className="flex justify-between items-center mb-1.5">
                <span className={`font-mono text-xs font-bold ${isToday ? "text-cyan-400" : "text-slate-400"}`}>
                  {dayNum}
                </span>
                {dayContests.length > 0 && (
                  <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                )}
              </div>

              <div className="space-y-1.5 overflow-y-auto max-h-[80px]">
                {dayContests.map((c) => (
                  <a
                    key={c.id}
                    href={c.url}
                    target="_blank"
                    rel="noreferrer"
                    className={`block p-1.5 rounded-lg border text-[10px] font-semibold leading-tight truncate transition hover:opacity-90 ${
                      PLATFORM_COLOR[c.platform] || "bg-violet-500/10 text-violet-400 border-violet-500/30"
                    }`}
                    title={c.name}
                  >
                    <div className="truncate font-bold">{c.name}</div>
                    <div className="text-[9px] opacity-80 font-mono mt-0.5">
                      {new Date(c.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </a>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

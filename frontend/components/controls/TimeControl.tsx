'use client'

import { useState } from 'react'
import { useStore } from '@/lib/store'
import { Calendar, Clock, ChevronLeft, ChevronRight } from 'lucide-react'
import { format, addDays, subDays } from 'date-fns'
import { motion, AnimatePresence } from 'framer-motion'

export function TimeControl() {
  const { selectedDate, setSelectedDate } = useStore()
  const [isOpen, setIsOpen] = useState(false)

  const handlePreviousDay = () => {
    setSelectedDate(subDays(selectedDate, 1))
  }

  const handleNextDay = () => {
    setSelectedDate(addDays(selectedDate, 1))
  }

  const handleToday = () => {
    setSelectedDate(new Date())
  }

  const isToday = format(selectedDate, 'yyyy-MM-dd') === format(new Date(), 'yyyy-MM-dd')

  return (
    <div className="fixed bottom-4 right-4 z-30">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-lg shadow-xl overflow-hidden"
      >
        <div className="flex items-center gap-2 p-3">
          {/* Previous Day */}
          <button
            onClick={handlePreviousDay}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="Previous day"
          >
            <ChevronLeft className="w-5 h-5 text-gray-600" />
          </button>

          {/* Current Date Display */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="flex items-center gap-2 px-4 py-2 hover:bg-gray-50 rounded-lg transition-colors"
          >
            <Calendar className="w-5 h-5 text-ocean-600" />
            <div className="text-left">
              <div className="text-sm font-medium text-gray-900">
                {format(selectedDate, 'MMM d, yyyy')}
              </div>
              <div className="text-xs text-gray-500">
                {format(selectedDate, 'EEEE')}
              </div>
            </div>
          </button>

          {/* Next Day */}
          <button
            onClick={handleNextDay}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="Next day"
          >
            <ChevronRight className="w-5 h-5 text-gray-600" />
          </button>

          {/* Today Button */}
          {!isToday && (
            <button
              onClick={handleToday}
              className="ml-2 px-3 py-1 bg-ocean-500 hover:bg-ocean-600 text-white 
                       text-xs font-medium rounded-lg transition-colors"
            >
              Today
            </button>
          )}
        </div>

        {/* Quick Date Selector */}
        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="border-t overflow-hidden"
            >
              <div className="p-3 space-y-1">
                <div className="text-xs font-medium text-gray-500 mb-2">Quick select:</div>
                {[0, 1, 2, 3, 7].map((days) => {
                  const date = addDays(new Date(), days)
                  return (
                    <button
                      key={days}
                      onClick={() => {
                        setSelectedDate(date)
                        setIsOpen(false)
                      }}
                      className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 
                               rounded-lg transition-colors"
                    >
                      <div className="font-medium">
                        {days === 0 ? 'Today' : days === 1 ? 'Tomorrow' : `+${days} days`}
                      </div>
                      <div className="text-xs text-gray-500">
                        {format(date, 'MMM d, yyyy')}
                      </div>
                    </button>
                  )
                })}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  )
}

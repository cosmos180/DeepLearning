package timestamp

import com.sun.jmx.snmp.Timestamp
import java.text.SimpleDateFormat
import java.text.DateFormat
import java.util.*
import jdk.nashorn.internal.objects.NativeDate.getTime
import jdk.nashorn.internal.objects.NativeDate.getTime






class TimestampPrinter {
    companion object {
        fun strToTimestamp() {
            val timeStr = "20190722100333"
            val sdf = SimpleDateFormat("yyyyMMddHHmmss")
            val dateObj = sdf.parse(timeStr)
            System.out.println(dateObj.time)
//            val dateStr = "20190722100333"
//            var date = Date()
//            //注意format的格式要与日期String的格式相匹配
//            val sdf = SimpleDateFormat("yyyyMMddHHmmss")
//            try {
//                date = sdf.parse(dateStr)
//                val ts = Timestamp(date.time)
//                print(ts.dateTime)
//            } catch (e: Exception) {
//                e.printStackTrace()
//            }
        }
    }
}
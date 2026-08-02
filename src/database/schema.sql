
        PRAGMA foreign_keys = ON;

        ------------------------------------------------------------
        -- Sleep: one row per night
        ------------------------------------------------------------
        CREATE TABLE IF NOT EXISTS Sleep (
            calendarDate TEXT PRIMARY KEY,

            sleepStartTimestampGMT TEXT NOT NULL,
            sleepEndTimestampGMT   TEXT NOT NULL,

            deepSleepSeconds       INTEGER,
            lightSleepSeconds      INTEGER,
            remSleepSeconds        INTEGER,
            awakeSleepSeconds      INTEGER,
            totalSleepSeconds      INTEGER,

            averageRespiration     REAL,
            lowestRespiration      REAL,
            highestRespiration     REAL,

            awakeCount             INTEGER,
            avgSleepStress         REAL,

            overallScore           INTEGER,
            qualityScore           INTEGER,
            durationScore          INTEGER,
            recoveryScore          INTEGER,
            deepScore              INTEGER,
            remScore               INTEGER,
            lightScore             INTEGER,
            awakeningsCountScore   INTEGER,
            awakeTimeScore         INTEGER,
            combinedAwakeScore     INTEGER,
            restfulnessScore       INTEGER,
            interruptionsScore     INTEGER,

            feedback               TEXT,

            averageSPO2            REAL,
            averageHR              REAL,
            lowestSPO2             REAL
        );

        ------------------------------------------------------------
        -- DailySummary: one row per day
        ------------------------------------------------------------
        CREATE TABLE IF NOT EXISTS DailySummary (
            calendarDate TEXT PRIMARY KEY,

            activeKilocalories          INTEGER,
            bmrKilocalories             INTEGER,
            totalSteps                  INTEGER,
            totalDistanceMeters         INTEGER,

            highlyActiveSeconds         INTEGER,
            activeSeconds               INTEGER,
            moderateIntensityMinutes    INTEGER,
            vigorousIntensityMinutes    INTEGER,

            minHeartRate                REAL,
            maxHeartRate                REAL,
            currentDayRestingHeartRate  REAL,
            minAvgHeartRate             REAL,
            maxAvgHeartRate             REAL,

            averageSpo2Value            REAL,
            lowestSpo2Value             REAL,

            sweatLossInML               REAL,

            highestRespirationValue     REAL,
            lowestRespirationValue      REAL, 
            avgRespirationValue         REAL,

            charged                     REAL,
            drained                     REAL,
            endBattery                  REAL,
            minBattery                  REAL,
            maxBattery                  REAL,

            averageStressLevel          REAL,
            maxStressLevel              REAL,
            lowStressDuration           REAL,
            mediumStressDuration        REAL,
            highStressDuration          REAL
        );

        ------------------------------------------------------------
        -- FitnessTrends: one row per day
        ------------------------------------------------------------
        CREATE TABLE IF NOT EXISTS FitnessTrends(
            calendarDate TEXT PRIMARY KEY,

            vo2MaxValue               REAL,
            maxMet                    REAL,

            raceTime5K                REAL,
            raceTime10K               REAL,
            raceTimeHalf              REAL,
            raceTimeMarathon          REAL,

            weeklyTrainingLoadSum     REAL,

            trainingStatus            TEXT,
            fitnessLevelTrend         TEXT,

            FOREIGN KEY(calendarDate) REFERENCES DailySummary(calendarDate)
        );

        ------------------------------------------------------------
        -- ActivitySummary: one row per activity
        ------------------------------------------------------------
        CREATE TABLE IF NOT EXISTS ActivitySummary (
            activity_id INTEGER PRIMARY KEY AUTOINCREMENT,

            startTimeGmt INTEGER UNIQUE NOT NULL,
            calendarDate TEXT NOT NULL,
            start_time TEXT,

            activity_type TEXT,

            durationSeconds INTEGER,
            distanceMeters REAL,

            ratio_time_max_hr REAL,
            ratio_time_avg_hr REAL,
            hr_volatility REAL,
            hr_derivative REAL,
            hr_smoothness REAL,
            hr_oscillation REAL,
            hr_drift REAL,
            meters_per_beat REAL,
            plateau_seconds INTEGER,
            hr_pace_coupling REAL,
            start_hr_offset REAL,

            cadence_std REAL,
            cadence_cv REAL,
            cadence_drift REAL,
            cadence_derivative REAL,
            cadence_smoothness REAL,
            cadence_speed_coupling REAL,
            cadence_hr_coupling REAL,
            steps_per_meter REAL,
            running_start_cadence REAL,

            avg_speed REAL,
            max_speed REAL,
            speed_std REAL,
            speed_cv REAL,
            speed_drift REAL,
            speed_derivative REAL,
            speed_smoothness REAL,
            speed_oscillation REAL,
            speed_hr_coupling REAL,
            speed_cadence_coupling REAL,
            running_start_speed REAL,

            stride_std REAL,
            stride_cv REAL,
            stride_drift REAL,
            stride_derivative REAL,
            stride_smoothness REAL,
            stride_oscillation REAL,
            stride_speed_coupling REAL,
            stride_hr_coupling REAL,
            running_start_stride REAL,

            avgHr REAL,
            maxHr REAL,
            avgRunCadence REAL,
            maxRunCadence REAL,
            avgStrideLength REAL,
            steps REAL,

            activityTrainingLoad REAL,
            aerobicTrainingEffect REAL,
            anaerobicTrainingEffect REAL,
            trainingEffectLabel TEXT,

            vigorousIntensityMinutes REAL,
            moderateIntensityMinutes REAL,

            maxTemperature REAL,
            minTemperature REAL,

            FOREIGN KEY(calendarDate) REFERENCES DailySummary(calendarDate)
        );

        ------------------------------------------------------------
        -- Indexes for fast analytics
        ------------------------------------------------------------
        CREATE INDEX IF NOT EXISTS idx_activity_date ON ActivitySummary(calendarDate);
        CREATE INDEX IF NOT EXISTS idx_activity_type ON ActivitySummary(activity_type);
        CREATE INDEX IF NOT EXISTS idx_activity_start ON ActivitySummary(startTimeGmt);


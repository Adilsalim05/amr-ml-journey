Day 25 — What trimming does and doesn't fix

This is a reading/reflection day, so don't run any commands yet.

Your task is to write a short methods-style reflection covering three things:

1. What SLIDINGWINDOW did

You used:

SLIDINGWINDOW:4:20

Interpret it precisely:

Trimmomatic examines the read using a 4-base sliding window.
When the average quality within the window falls below Q20, trimming occurs at that point.
Thus, poor-quality sequence toward the end of a read can be removed.

Don't say simply "it removes low-quality bases." Explain the window + threshold mechanism.

2. What MINLEN:25 did

You used:

MINLEN:25

After trimming, reads shorter than 25 bases were discarded.

This is important because it explains why your sequence-length distribution changed. A changed length distribution is expected after quality trimming and minimum-length filtering.

3. What ILLUMINACLIP did

You used:

ILLUMINACLIP:NexteraPE-PE.fa:2:40:15

Explain that adapter sequences originate from the library-preparation process. When an insert is shorter than the sequencing read length, the sequencer eventually reads through the biological insert and into the adapter sequence.

Your reflection should therefore distinguish:

biological sequence → sequencing → library adapter contamination → computational removal

And explain why adapter contamination can interfere with downstream analyses.

4. State one limitation

Your key limitation should be something like:

Trimmomatic does not necessarily remove every instance of adapter contamination or solve every read-quality problem; residual 3′ adapter contamination may require a specialized adapter-trimming approach such as cutadapt.

This is a good scientific habit: don't treat a tool as a black box that "fixes the data."



### Day 25 — What Trimming Does and Doesn't Fix

On Day 25, I applied Trimmomatic to the paired-end reads of sample SRR2589044 (`SRR2589044_1` and `SRR2589044_2`). These are the two mate files generated from the same sequencing library, representing the forward and reverse reads of each paired-end fragment. I used the Nextera adapter sequence file provided with Trimmomatic to identify and remove adapter contamination. The `SLIDINGWINDOW:4:20` setting removes sequence when the average quality within a four-base window falls below Q20, while `MINLEN:25` discards reads that become shorter than 25 bases after trimming.

Before trimming, the FastQC report identified adapter contamination as a problem. After Trimmomatic processing, the adapter-content result improved substantially, demonstrating that the adapter-removal step was effective for this dataset. Approximately 79% of the input sequence/read output was retained after processing, which provides sufficient data to proceed with downstream analysis. The sequence-length distribution changed after trimming, as expected, because low-quality or adapter-contaminated portions were removed and reads falling below the minimum length threshold were discarded.

However, trimming does not guarantee that every sequencing-quality problem is corrected. Residual adapter contamination or other problematic sequence can remain after Trimmomatic processing and may require a specialized tool such as cutadapt. Therefore, the appropriate way to evaluate trimming is not simply to assume that the reads are now "clean," but to perform FastQC again and verify which specific quality problems improved and which, if any, remain.
. 

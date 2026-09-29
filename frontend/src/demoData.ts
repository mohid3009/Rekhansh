// Authentic pilot dataset for Bond Gavhan village, Nanded, Maharashtra (DoLR PS-26010)
export interface DemoParcel {
  id: string;
  survey_number: string;
  ror_owner_name: string;
  source: string;
  recorded_area_ha: number;
  current_area_ha: number;
  area_delta_pct: number;
  triage_state: 'CLEARED' | 'FLAGGED' | 'INSUFFICIENT_EVIDENCE';
  reason_codes: string[];
  match_type: 'ONE_TO_ONE' | 'SPLIT' | 'MERGE' | 'NO_MATCH';
  match_confidence: number;
  asbd_m: number;
  occlusion_fraction: number;
  support_ratio_pct: number;
  verification_status: 'UNVERIFIED' | 'CONFIRMED' | 'CORRECTED' | 'ESCALATED';
  version_number: number;
  current_hash: string;
  parent_hash: string;
  geometry: {
    type: 'Polygon';
    coordinates: number[][][];
  };
  bbox: number[];
}

export const DEMO_VILLAGE = {
  id: 'VIL-BOND-GAVHAN',
  name: 'Bond Gavhan (बोंड गव्हाण)',
  district: 'Nanded',
  taluka: 'Mahur',
  state: 'Maharashtra',
  gis_code: 'RVM1501271500010190910000',
  total_parcels: 30,
  total_area_ha: 138.45,
  center: [19.885, 78.088] as [number, number],
  bounds: [[19.878, 78.079], [19.891, 78.100]] as [[number, number], [number, number]]
};

export const DEMO_PARCELS: DemoParcel[] = [
  {
    "id": "P-001",
    "survey_number": "1",
    "ror_owner_name": "Ramesh Tukaram Patil",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 5.2,
    "current_area_ha": 5.12,
    "area_delta_pct": 1.54,
    "triage_state": "CLEARED",
    "reason_codes": [
      "CLEAR_BOUNDARY"
    ],
    "match_type": "ONE_TO_ONE",
    "match_confidence": 0.88,
    "asbd_m": 0.25,
    "occlusion_fraction": 0.02,
    "support_ratio_pct": 82.0,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "333553dc572dba88ab15b87e3b5d7c9685a852822e6ec9f834384c6d448ca4e2",
    "parent_hash": "b7b48ebb391f1d83dc1ecad5a77cb863bcc6523251791196a3be408894476a78",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0918658,
            19.8829513
          ],
          [
            78.091949,
            19.8818433
          ],
          [
            78.0959339,
            19.8812972
          ],
          [
            78.0962357,
            19.8823856
          ],
          [
            78.0929166,
            19.8827328
          ],
          [
            78.0918658,
            19.8829513
          ]
        ]
      ]
    },
    "bbox": [
      78.09182067731605,
      19.881288063450157,
      78.09625994911315,
      19.882952571483656
    ]
  },
  {
    "id": "P-010",
    "survey_number": "10",
    "ror_owner_name": "Sunita Suresh Deshmukh",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 2.66,
    "current_area_ha": 2.64,
    "area_delta_pct": 0.75,
    "triage_state": "CLEARED",
    "reason_codes": [
      "CLEAR_BOUNDARY"
    ],
    "match_type": "ONE_TO_ONE",
    "match_confidence": 0.9,
    "asbd_m": 0.37,
    "occlusion_fraction": 0.04,
    "support_ratio_pct": 85.2,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "566a9f22011a78d3479692b85b6f55627c7449bf2433d8d4fef3d589d07c4acd",
    "parent_hash": "ec2324066f3af99a17017d6433400142e4e5685faba0925be2038494cd8cd2c6",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0886854,
            19.8842392
          ],
          [
            78.0882675,
            19.8835356
          ],
          [
            78.0918581,
            19.8829563
          ],
          [
            78.0917814,
            19.883578
          ],
          [
            78.0886854,
            19.8842392
          ]
        ]
      ]
    },
    "bbox": [
      78.08825611507002,
      19.88295222986062,
      78.09189508033235,
      19.88424627459074
    ]
  },
  {
    "id": "P-011",
    "survey_number": "11",
    "ror_owner_name": "Ganesh Vitthal Shinde",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 5.44,
    "current_area_ha": 5.33,
    "area_delta_pct": 2.02,
    "triage_state": "INSUFFICIENT_EVIDENCE",
    "reason_codes": [
      "OCCLUSION_EXCEEDS_LIMIT",
      "TREE_CANOPY_HIGH"
    ],
    "match_type": "ONE_TO_ONE",
    "match_confidence": 0.62,
    "asbd_m": 2.85,
    "occlusion_fraction": 0.42,
    "support_ratio_pct": 45.2,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "434e0a116052c351b73e67b886b47f37d10ab1338dff741758d845fef44b4ef0",
    "parent_hash": "239eb98001565dc5926819805a74c42e4c9c47163561f48e8194b85051dbc27f",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0892821,
            19.8853543
          ],
          [
            78.0886833,
            19.8842466
          ],
          [
            78.0917859,
            19.8835831
          ],
          [
            78.0918192,
            19.884927
          ],
          [
            78.0922018,
            19.8856524
          ],
          [
            78.0909291,
            19.8859335
          ],
          [
            78.0905548,
            19.8853937
          ],
          [
            78.0900807,
            19.8851913
          ],
          [
            78.0892821,
            19.8853543
          ]
        ]
      ]
    },
    "bbox": [
      78.08867215992288,
      19.883570020478587,
      78.0922211903955,
      19.885969111563387
    ]
  },
  {
    "id": "P-012",
    "survey_number": "12",
    "ror_owner_name": "Ananda Laxman Jadhav",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 2.34,
    "current_area_ha": 2.36,
    "area_delta_pct": 0.85,
    "triage_state": "CLEARED",
    "reason_codes": [
      "CLEAR_BOUNDARY"
    ],
    "match_type": "ONE_TO_ONE",
    "match_confidence": 0.93,
    "asbd_m": 0.61,
    "occlusion_fraction": 0.08,
    "support_ratio_pct": 91.6,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "e7efefa3a85308bec5bd51b26f92f04ae72d52cb92c08e22ff488c5f111fd553",
    "parent_hash": "042fbd910a934e1fe4d68a915a0fee2c9ee5977a6b5b3b6317ffc01387abd982",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0896437,
            19.8870118
          ],
          [
            78.0892785,
            19.885358
          ],
          [
            78.0900559,
            19.8851844
          ],
          [
            78.0905467,
            19.885384
          ],
          [
            78.0909275,
            19.885931
          ],
          [
            78.0908175,
            19.8866211
          ],
          [
            78.0908333,
            19.8867514
          ],
          [
            78.0896437,
            19.8870118
          ]
        ]
      ]
    },
    "bbox": [
      78.08927721952652,
      19.885165545178786,
      78.09095234476769,
      19.88701760227653
    ]
  },
  {
    "id": "P-013",
    "survey_number": "13",
    "ror_owner_name": "Vikas Pandurang Gaikwad",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 2.43,
    "current_area_ha": 2.47,
    "area_delta_pct": 1.65,
    "triage_state": "CLEARED",
    "reason_codes": [
      "CLEAR_BOUNDARY"
    ],
    "match_type": "ONE_TO_ONE",
    "match_confidence": 0.94,
    "asbd_m": 0.73,
    "occlusion_fraction": 0.02,
    "support_ratio_pct": 94.8,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "e009f13ba90e0c287ba7e181ec615816b15097fbf577b98c4e830246246905f1",
    "parent_hash": "483fed939fb91a635d3ad772623db4ba9c8104180e3d6cfb071eef3f37443639",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0903205,
            19.8889116
          ],
          [
            78.0896412,
            19.8870201
          ],
          [
            78.0908312,
            19.8867536
          ],
          [
            78.0910592,
            19.8874251
          ],
          [
            78.091392,
            19.8872559
          ],
          [
            78.0915562,
            19.8878095
          ],
          [
            78.0910318,
            19.8882043
          ],
          [
            78.0903205,
            19.8889116
          ]
        ]
      ]
    },
    "bbox": [
      78.08963966201897,
      19.886736500642833,
      78.09158504915159,
      19.888923605719732
    ]
  },
  {
    "id": "P-014",
    "survey_number": "14",
    "ror_owner_name": "Meena Balaji Kadam",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 5.68,
    "current_area_ha": 5.62,
    "area_delta_pct": 1.06,
    "triage_state": "FLAGGED",
    "reason_codes": [
      "SPLIT_DETECTED"
    ],
    "match_type": "SPLIT",
    "match_confidence": 0.81,
    "asbd_m": 1.95,
    "occlusion_fraction": 0.05,
    "support_ratio_pct": 74.0,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "342ea6b2c87eba7812b9b338cf4f096681154d3b44e23ca2f7859837f836c2e4",
    "parent_hash": "bcaa91f7286a56d9e7fecd4672b57e9440e6995b17649cd97a5b047e7091329a",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0902232,
            19.8886575
          ],
          [
            78.0890926,
            19.8892146
          ],
          [
            78.0876914,
            19.885954
          ],
          [
            78.089273,
            19.8853694
          ],
          [
            78.0896399,
            19.8870408
          ],
          [
            78.0902232,
            19.8886575
          ]
        ]
      ]
    },
    "bbox": [
      78.08767733265181,
      19.88533897364765,
      78.090243266679,
      19.889235931063055
    ]
  },
  {
    "id": "P-015",
    "survey_number": "15",
    "ror_owner_name": "Santosh Digambar Joshi",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 6.42,
    "current_area_ha": 6.37,
    "area_delta_pct": 0.78,
    "triage_state": "CLEARED",
    "reason_codes": [
      "CLEAR_BOUNDARY"
    ],
    "match_type": "ONE_TO_ONE",
    "match_confidence": 0.97,
    "asbd_m": 0.25,
    "occlusion_fraction": 0.06,
    "support_ratio_pct": 85.2,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "a6d20a85e398da17d50e0ef9176d742ff2eab0226ff9d98f972b8ff0ddc3395e",
    "parent_hash": "737bbf191cb35ea1f12fd35cb691641386f1c2eff98671806cd5b09573a23633",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0890861,
            19.8892154
          ],
          [
            78.0881599,
            19.8894607
          ],
          [
            78.0871442,
            19.8895283
          ],
          [
            78.0863904,
            19.88634
          ],
          [
            78.0876872,
            19.8859679
          ],
          [
            78.0890861,
            19.8892154
          ]
        ]
      ]
    },
    "bbox": [
      78.08637554055747,
      19.885931287635906,
      78.08910098204092,
      19.8895395944846
    ]
  },
  {
    "id": "P-016",
    "survey_number": "16",
    "ror_owner_name": "Rajendra Bapurao Chavan",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 5.81,
    "current_area_ha": 5.81,
    "area_delta_pct": 0.0,
    "triage_state": "CLEARED",
    "reason_codes": [
      "CLEAR_BOUNDARY"
    ],
    "match_type": "ONE_TO_ONE",
    "match_confidence": 0.88,
    "asbd_m": 0.37,
    "occlusion_fraction": 0.08,
    "support_ratio_pct": 88.4,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "12deabc6fd9defe686275d8e939417514ab473e267f517b0cc91cde3c4dbd38f",
    "parent_hash": "ccc3e5f52c91f792c378a34eca4cf1e53d82a6612795e97f67cfcee68acf73b8",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0821371,
            19.8869494
          ],
          [
            78.0821709,
            19.8863392
          ],
          [
            78.0844359,
            19.8861254
          ],
          [
            78.088932,
            19.8847694
          ],
          [
            78.0892532,
            19.8853587
          ],
          [
            78.0877488,
            19.8859324
          ],
          [
            78.0842838,
            19.8868816
          ],
          [
            78.0825935,
            19.8869755
          ],
          [
            78.0821371,
            19.8869494
          ]
        ]
      ]
    },
    "bbox": [
      78.0820976690078,
      19.884757206082014,
      78.08930951325821,
      19.886982464339535
    ]
  },
  {
    "id": "P-017",
    "survey_number": "17",
    "ror_owner_name": "Usha Prakash Rathod",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 5.4,
    "current_area_ha": 5.44,
    "area_delta_pct": 0.74,
    "triage_state": "CLEARED",
    "reason_codes": [
      "CLEAR_BOUNDARY"
    ],
    "match_type": "ONE_TO_ONE",
    "match_confidence": 0.9,
    "asbd_m": 0.49,
    "occlusion_fraction": 0.02,
    "support_ratio_pct": 91.6,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "25a51dce920cef0d2c2e6552b60d1b6d6d7bba5b7e98dd098b1a3795ca6adbd2",
    "parent_hash": "4f8b3fa9e824127af8f8f5d7f16c22b34e5c878d50de87916dccfbb11b74eb21",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0821703,
            19.8863364
          ],
          [
            78.0822024,
            19.8857216
          ],
          [
            78.0857475,
            19.8850479
          ],
          [
            78.088667,
            19.8842463
          ],
          [
            78.0889237,
            19.8847627
          ],
          [
            78.0844321,
            19.88612
          ],
          [
            78.0821703,
            19.8863364
          ]
        ]
      ]
    },
    "bbox": [
      78.08213284020123,
      19.88423483780941,
      78.08897716754969,
      19.886333075005194
    ]
  },
  {
    "id": "P-018",
    "survey_number": "18",
    "ror_owner_name": "Nitin Ramrao Pawar",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 6.12,
    "current_area_ha": 6.22,
    "area_delta_pct": 1.63,
    "triage_state": "CLEARED",
    "reason_codes": [
      "CLEAR_BOUNDARY"
    ],
    "match_type": "ONE_TO_ONE",
    "match_confidence": 0.91,
    "asbd_m": 0.61,
    "occlusion_fraction": 0.04,
    "support_ratio_pct": 94.8,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "f56337d4c1ed2169d0bc4b4b1736ee0b99873ed90be932eaa0f7bace17e9b280",
    "parent_hash": "c87f6586f652bbd99be7cecf824b7bcb16c82a6790eae23c99ed29aee351e14f",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0822071,
            19.8857217
          ],
          [
            78.0820982,
            19.8846666
          ],
          [
            78.0826113,
            19.8847329
          ],
          [
            78.0860625,
            19.8838467
          ],
          [
            78.088068,
            19.8831714
          ],
          [
            78.0886587,
            19.8842386
          ],
          [
            78.085736,
            19.8850464
          ],
          [
            78.0822071,
            19.8857217
          ]
        ]
      ]
    },
    "bbox": [
      78.082077500491,
      19.883151325418805,
      78.08871054798131,
      19.88572370898623
    ]
  },
  {
    "id": "P-019",
    "survey_number": "19",
    "ror_owner_name": "Kavita Ashok More",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 7.64,
    "current_area_ha": 7.03,
    "area_delta_pct": 7.98,
    "triage_state": "FLAGGED",
    "reason_codes": [
      "AREA_DIFF_EXCEEDS_TOLERANCE"
    ],
    "match_type": "ONE_TO_ONE",
    "match_confidence": 0.78,
    "asbd_m": 2.15,
    "occlusion_fraction": 0.08,
    "support_ratio_pct": 68.5,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "c2a4007ab820b2fdb5f873f1a35a39e9e81ec7129c77022a85f9f7fa10ec97cc",
    "parent_hash": "4ca440e9e61dc8af0a52f33598de27235cbed09119232eb1cad4a04431d9c130",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0824802,
            19.8847137
          ],
          [
            78.0822456,
            19.883619
          ],
          [
            78.0856815,
            19.8827482
          ],
          [
            78.0875857,
            19.8820889
          ],
          [
            78.0880687,
            19.8831649
          ],
          [
            78.0860679,
            19.8838367
          ],
          [
            78.0824802,
            19.8847137
          ]
        ]
      ]
    },
    "bbox": [
      78.08222718559398,
      19.882074353316767,
      78.08811470345906,
      19.88472825256778
    ]
  },
  {
    "id": "P-002",
    "survey_number": "2",
    "ror_owner_name": "Dnyaneshwar Maruti Sonwane",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 4.42,
    "current_area_ha": 4.38,
    "area_delta_pct": 0.9,
    "triage_state": "CLEARED",
    "reason_codes": [
      "CLEAR_BOUNDARY"
    ],
    "match_type": "ONE_TO_ONE",
    "match_confidence": 0.94,
    "asbd_m": 0.85,
    "occlusion_fraction": 0.08,
    "support_ratio_pct": 85.2,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "64d7ca2fc81d5afa3a0b832bf56a45198733e347a2d9dd6f0daf4b593a15a4a2",
    "parent_hash": "55268bf81f4b46be2e227c0da71234def9bb8f80f4e76db15923d992d5f77d81",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0962451,
            19.8823851
          ],
          [
            78.0959499,
            19.8812998
          ],
          [
            78.0990759,
            19.880637
          ],
          [
            78.099623,
            19.881685
          ],
          [
            78.0975824,
            19.882062
          ],
          [
            78.0975303,
            19.8821407
          ],
          [
            78.0962451,
            19.8823851
          ]
        ]
      ]
    },
    "bbox": [
      78.095938293268,
      19.8806231837043,
      78.09964326150721,
      19.882390622413247
    ]
  },
  {
    "id": "P-020",
    "survey_number": "20",
    "ror_owner_name": "Savita Baburao Mane",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 6.44,
    "current_area_ha": 6.44,
    "area_delta_pct": 0.0,
    "triage_state": "CLEARED",
    "reason_codes": [
      "CLEAR_BOUNDARY"
    ],
    "match_type": "ONE_TO_ONE",
    "match_confidence": 0.95,
    "asbd_m": 0.25,
    "occlusion_fraction": 0.02,
    "support_ratio_pct": 88.4,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "af9be94dfa5e40545a387528ec30f80ca5265560b743f014e3f3a65a02b1e282",
    "parent_hash": "9a638507b9759d658a639efd978cc2feb08978acabbe9f879cce7099a22ace95",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.080945,
            19.8838122
          ],
          [
            78.0807834,
            19.8832918
          ],
          [
            78.0873433,
            19.8812472
          ],
          [
            78.0875857,
            19.882092
          ],
          [
            78.0856791,
            19.8827409
          ],
          [
            78.0823991,
            19.8835857
          ],
          [
            78.0811065,
            19.8838367
          ],
          [
            78.080945,
            19.8838122
          ]
        ]
      ]
    },
    "bbox": [
      78.08074569784456,
      19.881226761377377,
      78.08763954761763,
      19.88383871532888
    ]
  },
  {
    "id": "P-021",
    "survey_number": "21",
    "ror_owner_name": "Vishnu Narayan Wagh",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 8.12,
    "current_area_ha": 8.36,
    "area_delta_pct": 2.96,
    "triage_state": "FLAGGED",
    "reason_codes": [
      "NEIGHBOR_OVERLAP_EXCEEDS_TOLERANCE"
    ],
    "match_type": "MERGE",
    "match_confidence": 0.76,
    "asbd_m": 2.3,
    "occlusion_fraction": 0.09,
    "support_ratio_pct": 65.0,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "219921042a11e7688d60af18e472b99c8d4276be8aed705a6ee047a6da0bbd50",
    "parent_hash": "46bd6cdc83a69fe78e920f4ebbddaf7538a441dc7ae0dfd1e3b42b3d5c218f36",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0807741,
            19.8832843
          ],
          [
            78.080679,
            19.8824501
          ],
          [
            78.0831196,
            19.8815332
          ],
          [
            78.0846411,
            19.8808301
          ],
          [
            78.0870817,
            19.8803613
          ],
          [
            78.0872719,
            19.8812782
          ],
          [
            78.0807741,
            19.8832843
          ]
        ]
      ]
    },
    "bbox": [
      78.08064200605088,
      19.880345229270354,
      78.087403998135,
      19.88328655030651
    ]
  },
  {
    "id": "P-022",
    "survey_number": "22",
    "ror_owner_name": "Pooja Sanjay Kale",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 1.26,
    "current_area_ha": 1.28,
    "area_delta_pct": 1.59,
    "triage_state": "CLEARED",
    "reason_codes": [
      "CLEAR_BOUNDARY"
    ],
    "match_type": "ONE_TO_ONE",
    "match_confidence": 0.88,
    "asbd_m": 0.49,
    "occlusion_fraction": 0.06,
    "support_ratio_pct": 94.8,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "ddbf61eb39340bfd04ae0b78b17f3a26fa933dd5ab37a879364ae82fb996603f",
    "parent_hash": "33786f5d94a10736644a8f61efd347e6eb2593e0592122ce7d1e0244dfaedf0a",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0802804,
            19.8838658
          ],
          [
            78.0801585,
            19.8833042
          ],
          [
            78.0796048,
            19.8828973
          ],
          [
            78.0795455,
            19.8828166
          ],
          [
            78.0806759,
            19.8824501
          ],
          [
            78.0807352,
            19.8831462
          ],
          [
            78.0809395,
            19.883812
          ],
          [
            78.0802804,
            19.8838658
          ]
        ]
      ]
    },
    "bbox": [
      78.0795377950803,
      19.88244222221698,
      78.08094390730407,
      19.883876989572805
    ]
  },
  {
    "id": "P-023",
    "survey_number": "23",
    "ror_owner_name": "Dilip Govind Solanke",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 2.2,
    "current_area_ha": 2.16,
    "area_delta_pct": 1.82,
    "triage_state": "CLEARED",
    "reason_codes": [
      "CLEAR_BOUNDARY"
    ],
    "match_type": "ONE_TO_ONE",
    "match_confidence": 0.9,
    "asbd_m": 0.61,
    "occlusion_fraction": 0.08,
    "support_ratio_pct": 82.0,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "6f9933f84068823beeccbf397f2f1171dde9b18a9d5d2fea3f74ae35a65c8743",
    "parent_hash": "dc329a72c7a4a137480cee525f1fefa20a9cadecc67b7b2c199a80266a543229",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0813209,
            19.8848162
          ],
          [
            78.0804288,
            19.8844313
          ],
          [
            78.0802784,
            19.8838683
          ],
          [
            78.0809267,
            19.8838137
          ],
          [
            78.0811083,
            19.8838367
          ],
          [
            78.0822493,
            19.8836155
          ],
          [
            78.0824827,
            19.8847128
          ],
          [
            78.0820937,
            19.8846611
          ],
          [
            78.0813209,
            19.8848162
          ]
        ]
      ]
    },
    "bbox": [
      78.08027669427061,
      19.883608785393847,
      78.0824896324907,
      19.88483443157248
    ]
  },
  {
    "id": "P-024",
    "survey_number": "24",
    "ror_owner_name": "Archana Bharat Shinde",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 2.45,
    "current_area_ha": 0.0,
    "area_delta_pct": 100.0,
    "triage_state": "INSUFFICIENT_EVIDENCE",
    "reason_codes": [
      "NO_MATCHING_FIELD",
      "BOUNDARY_OBSCURED"
    ],
    "match_type": "NO_MATCH",
    "match_confidence": 0.12,
    "asbd_m": 5.4,
    "occlusion_fraction": 0.58,
    "support_ratio_pct": 15.0,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "97088cfd64eb94f7e11c2fc6f93cbdcede3ab3766fd0ac724c0bbcc999cd81e9",
    "parent_hash": "b49645d42d26bffc0506cce66ca361b9e89049350fd76e95f27a48a0bc0fb935",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0814282,
            19.8869059
          ],
          [
            78.0813204,
            19.8848228
          ],
          [
            78.0821011,
            19.8846663
          ],
          [
            78.0822111,
            19.8857133
          ],
          [
            78.0821464,
            19.8864742
          ],
          [
            78.0821357,
            19.886949
          ],
          [
            78.0814282,
            19.8869059
          ]
        ]
      ]
    },
    "bbox": [
      78.08131750547727,
      19.88465914777378,
      78.08223774451164,
      19.886961636607374
    ]
  },
  {
    "id": "P-025",
    "survey_number": "25",
    "ror_owner_name": "Pandhari Nath Suryavanshi",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 5.53,
    "current_area_ha": 5.53,
    "area_delta_pct": 0.0,
    "triage_state": "CLEARED",
    "reason_codes": [
      "CLEAR_BOUNDARY"
    ],
    "match_type": "ONE_TO_ONE",
    "match_confidence": 0.93,
    "asbd_m": 0.85,
    "occlusion_fraction": 0.04,
    "support_ratio_pct": 88.4,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "331d9a8dbfc1918f8fb0174bd0d796ca2242b8961aa72336124261dd07c2c5b7",
    "parent_hash": "2411e15d0c00a77341dfbc60319478d19c3029abea8ceea226c5130cbb774737",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0845506,
            19.8894307
          ],
          [
            78.0832812,
            19.8886009
          ],
          [
            78.0819304,
            19.8883037
          ],
          [
            78.0811167,
            19.8874801
          ],
          [
            78.0810923,
            19.8873067
          ],
          [
            78.0814259,
            19.8869166
          ],
          [
            78.0826058,
            19.8869847
          ],
          [
            78.0841356,
            19.8869104
          ],
          [
            78.0845506,
            19.8894307
          ]
        ]
      ]
    },
    "bbox": [
      78.08108961060661,
      19.886852584978776,
      78.08456144556641,
      19.889494728150517
    ]
  },
  {
    "id": "P-026",
    "survey_number": "26",
    "ror_owner_name": "Chandrakant Shivaji Salve",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 3.28,
    "current_area_ha": 3.31,
    "area_delta_pct": 0.91,
    "triage_state": "CLEARED",
    "reason_codes": [
      "CLEAR_BOUNDARY"
    ],
    "match_type": "ONE_TO_ONE",
    "match_confidence": 0.94,
    "asbd_m": 0.25,
    "occlusion_fraction": 0.06,
    "support_ratio_pct": 91.6,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "d25716481f4b434f16f5740b7df1113e9e19af45845eb8757b463d7c80b87939",
    "parent_hash": "024d4da866fa7d16e058be7cc5ee622b8d9c4285c5372a32e0a3cf05a23eab74",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0844744,
            19.8889302
          ],
          [
            78.0841419,
            19.8869093
          ],
          [
            78.0855118,
            19.88655
          ],
          [
            78.0858363,
            19.8886944
          ],
          [
            78.0844744,
            19.8889302
          ]
        ]
      ]
    },
    "bbox": [
      78.08413660369158,
      19.886536901699515,
      78.08584564725197,
      19.888932062617833
    ]
  },
  {
    "id": "P-027",
    "survey_number": "27",
    "ror_owner_name": "Suman Keshav Dhage",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 2.7,
    "current_area_ha": 2.56,
    "area_delta_pct": 5.19,
    "triage_state": "INSUFFICIENT_EVIDENCE",
    "reason_codes": [
      "LOW_AI_CONFIDENCE",
      "CLOUD_SHADOW_DETECTED"
    ],
    "match_type": "ONE_TO_ONE",
    "match_confidence": 0.54,
    "asbd_m": 3.1,
    "occlusion_fraction": 0.38,
    "support_ratio_pct": 48.0,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "165dfc8dec02c8429cc50358508d88a4e983b68f9c7545b351e1946a6dc1f3c5",
    "parent_hash": "8f2f97519d958d0fe5a036537fd44dd26bbe722d087a151d23c96ec115fe6210",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0858394,
            19.8886972
          ],
          [
            78.0855159,
            19.8865505
          ],
          [
            78.0863832,
            19.8863508
          ],
          [
            78.0869302,
            19.8885308
          ],
          [
            78.0858394,
            19.8886972
          ]
        ]
      ]
    },
    "bbox": [
      78.08551478100384,
      19.88633235435122,
      78.08693798679657,
      19.888699046575255
    ]
  },
  {
    "id": "P-028",
    "survey_number": "28",
    "ror_owner_name": "Maroti Eknath Ghuge",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 2.26,
    "current_area_ha": 2.22,
    "area_delta_pct": 1.77,
    "triage_state": "CLEARED",
    "reason_codes": [
      "CLEAR_BOUNDARY"
    ],
    "match_type": "ONE_TO_ONE",
    "match_confidence": 0.97,
    "asbd_m": 0.49,
    "occlusion_fraction": 0.02,
    "support_ratio_pct": 82.0,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "538be51fdd4fe86b7b9e691f5bc0eff3c33608dbd06ad61ea5cf42266288e26d",
    "parent_hash": "ed5b613e573d06e3e4ae0ddfdb6f8295dd08f90d456c85ca65415fd8e43b103e",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0865571,
            19.8901891
          ],
          [
            78.0853839,
            19.889803
          ],
          [
            78.0845592,
            19.8894355
          ],
          [
            78.0844708,
            19.8889306
          ],
          [
            78.0861938,
            19.8886522
          ],
          [
            78.0865571,
            19.8901891
          ]
        ]
      ]
    },
    "bbox": [
      78.08446915752748,
      19.88864355422767,
      78.08656362897167,
      19.890227451408194
    ]
  },
  {
    "id": "P-029",
    "survey_number": "29",
    "ror_owner_name": "Deepak Shankar Munde",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 1.31,
    "current_area_ha": 1.3,
    "area_delta_pct": 0.76,
    "triage_state": "CLEARED",
    "reason_codes": [
      "CLEAR_BOUNDARY"
    ],
    "match_type": "ONE_TO_ONE",
    "match_confidence": 0.88,
    "asbd_m": 0.61,
    "occlusion_fraction": 0.04,
    "support_ratio_pct": 85.2,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "f54e7a7ecebd6c1ea1f0b18edfad86326f71097062e0f359a75f70a2b883a6b5",
    "parent_hash": "8c31ad76d9e3b82de7f532bea65ad1ba2965850498dfb763c2e7c303d344ca9e",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0872494,
            19.8901735
          ],
          [
            78.0869484,
            19.8902507
          ],
          [
            78.0865636,
            19.8901938
          ],
          [
            78.0862034,
            19.8886529
          ],
          [
            78.0869336,
            19.888535
          ],
          [
            78.0871334,
            19.889397
          ],
          [
            78.0872494,
            19.8901735
          ]
        ]
      ]
    },
    "bbox": [
      78.08620012681374,
      19.888525558931274,
      78.08725267829676,
      19.89026022161497
    ]
  },
  {
    "id": "P-003",
    "survey_number": "3",
    "ror_owner_name": "Anita Mahadev Kakade",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 5.54,
    "current_area_ha": 6.04,
    "area_delta_pct": 9.03,
    "triage_state": "FLAGGED",
    "reason_codes": [
      "AREA_DIFF_EXCEEDS_TOLERANCE"
    ],
    "match_type": "ONE_TO_ONE",
    "match_confidence": 0.78,
    "asbd_m": 2.15,
    "occlusion_fraction": 0.08,
    "support_ratio_pct": 68.5,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "944d5d5429d7c2a69680b4ebaf4f02083a20737f96bf76a5f29119dc474c22ac",
    "parent_hash": "64afa75e145716698531f627b0c1e7255596c1a0f867feb1446ce610d5473b47",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0919578,
            19.8818402
          ],
          [
            78.091768,
            19.8812884
          ],
          [
            78.0967352,
            19.8804608
          ],
          [
            78.0986151,
            19.8800449
          ],
          [
            78.0990635,
            19.8806348
          ],
          [
            78.0960625,
            19.8812927
          ],
          [
            78.0919578,
            19.8818402
          ]
        ]
      ]
    },
    "bbox": [
      78.09174504228876,
      19.880030706352166,
      78.09910375672324,
      19.881841599588277
    ]
  },
  {
    "id": "P-030",
    "survey_number": "30",
    "ror_owner_name": "Pravin Ramdas Bodkhe",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 2.6,
    "current_area_ha": 2.65,
    "area_delta_pct": 1.92,
    "triage_state": "INSUFFICIENT_EVIDENCE",
    "reason_codes": [
      "OCCLUSION_EXCEEDS_LIMIT",
      "CANOPY_DISPUTE"
    ],
    "match_type": "ONE_TO_ONE",
    "match_confidence": 0.65,
    "asbd_m": 2.4,
    "occlusion_fraction": 0.35,
    "support_ratio_pct": 52.0,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "7f866a491577e352a4d1bd7ed5f5434c96fbe0536b1c5512b481e170768da0aa",
    "parent_hash": "5d2143884e5f8ee05ac508ed22da2f92526bad468cb85e438669de1914f06ca9",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0872476,
            19.8901723
          ],
          [
            78.0871497,
            19.8895317
          ],
          [
            78.0881516,
            19.889468
          ],
          [
            78.0890933,
            19.8892169
          ],
          [
            78.0902308,
            19.8886624
          ],
          [
            78.0903137,
            19.8889172
          ],
          [
            78.0894022,
            19.8899026
          ],
          [
            78.089018,
            19.8899663
          ],
          [
            78.0883249,
            19.8901723
          ],
          [
            78.0878654,
            19.890236
          ],
          [
            78.0872476,
            19.8901723
          ]
        ]
      ]
    },
    "bbox": [
      78.08713211138173,
      19.888653702918177,
      78.09034632940671,
      19.890252249122906
    ]
  },
  {
    "id": "P-004",
    "survey_number": "4",
    "ror_owner_name": "Shobha Vitthal Khandare",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 4.14,
    "current_area_ha": 4.21,
    "area_delta_pct": 1.69,
    "triage_state": "CLEARED",
    "reason_codes": [
      "CLEAR_BOUNDARY"
    ],
    "match_type": "ONE_TO_ONE",
    "match_confidence": 0.93,
    "asbd_m": 0.25,
    "occlusion_fraction": 0.02,
    "support_ratio_pct": 94.8,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "6a4360e83ed977f83676d895a927a3d976a019ba1956b578efcb2146e4ce5db6",
    "parent_hash": "ec08bfd135e2da1867336d49bda0eb6c6dc2401c7f272bf028f580c8d2e24224",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.091764,
            19.8812819
          ],
          [
            78.0916654,
            19.8808445
          ],
          [
            78.0920104,
            19.8807116
          ],
          [
            78.0943926,
            19.8803367
          ],
          [
            78.0980563,
            19.8796297
          ],
          [
            78.0986148,
            19.8800398
          ],
          [
            78.0967419,
            19.8804538
          ],
          [
            78.091764,
            19.8812819
          ]
        ]
      ]
    },
    "bbox": [
      78.09164351476942,
      19.879616642127218,
      78.09865316789987,
      19.88128323586477
    ]
  },
  {
    "id": "P-005",
    "survey_number": "5",
    "ror_owner_name": "Gopal Babarao Lahane",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 10.09,
    "current_area_ha": 10.29,
    "area_delta_pct": 1.98,
    "triage_state": "FLAGGED",
    "reason_codes": [
      "BOUNDARY_DISPLACEMENT_EXCEEDS_TOLERANCE"
    ],
    "match_type": "ONE_TO_ONE",
    "match_confidence": 0.74,
    "asbd_m": 2.65,
    "occlusion_fraction": 0.12,
    "support_ratio_pct": 62.0,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "b07f712fc33cd5eb998107415388a841df3e538ecb34e6828013b6fdb765d8de",
    "parent_hash": "246581d7685ecc6d8b4bdd5d311c7e28450f93cd8a23736e273ae8227bef148c",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0920373,
            19.8807081
          ],
          [
            78.0916919,
            19.8790117
          ],
          [
            78.095296,
            19.878358
          ],
          [
            78.0961069,
            19.8785158
          ],
          [
            78.0963922,
            19.8787243
          ],
          [
            78.097113,
            19.8789723
          ],
          [
            78.0974283,
            19.879395
          ],
          [
            78.098059,
            19.879626
          ],
          [
            78.094395,
            19.8803361
          ],
          [
            78.0920373,
            19.8807081
          ]
        ]
      ]
    },
    "bbox": [
      78.09168694154697,
      19.87830539625912,
      78.098094076589,
      19.88070993394344
    ]
  },
  {
    "id": "P-006",
    "survey_number": "6",
    "ror_owner_name": "Rohidas Madhav Kharat",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 1.67,
    "current_area_ha": 1.66,
    "area_delta_pct": 0.6,
    "triage_state": "CLEARED",
    "reason_codes": [
      "CLEAR_BOUNDARY"
    ],
    "match_type": "ONE_TO_ONE",
    "match_confidence": 0.95,
    "asbd_m": 0.49,
    "occlusion_fraction": 0.06,
    "support_ratio_pct": 85.2,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "4bdd2e4ddb50a6cfd20d472f3b478bcd7461f80211f4466942d32f477e427015",
    "parent_hash": "c81302c1c656d13131c3b35eb059074669fe8b3f783f8ffcdfdfcfccecd2eaa4",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0913086,
            19.880948
          ],
          [
            78.090773,
            19.8791714
          ],
          [
            78.0916953,
            19.8790112
          ],
          [
            78.0920315,
            19.8807053
          ],
          [
            78.0913086,
            19.880948
          ]
        ]
      ]
    },
    "bbox": [
      78.09076905763443,
      19.879000496596518,
      78.09203845315191,
      19.88095412720022
    ]
  },
  {
    "id": "P-007",
    "survey_number": "7",
    "ror_owner_name": "Mangala Bhagwan Pimple",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 7.74,
    "current_area_ha": 7.74,
    "area_delta_pct": 0.0,
    "triage_state": "CLEARED",
    "reason_codes": [
      "CLEAR_BOUNDARY"
    ],
    "match_type": "ONE_TO_ONE",
    "match_confidence": 0.97,
    "asbd_m": 0.61,
    "occlusion_fraction": 0.08,
    "support_ratio_pct": 88.4,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "5fca7995544dff5057ecd688283dfdc6be48fb85b1d0108da76d8395e547210b",
    "parent_hash": "e7731838340a5b33fec9966f60fe0644260c127ae7c839cd556292222fe79d80",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0876061,
            19.8820812
          ],
          [
            78.0871086,
            19.8803566
          ],
          [
            78.0893774,
            19.8798687
          ],
          [
            78.089258,
            19.8794977
          ],
          [
            78.0907606,
            19.8791747
          ],
          [
            78.091298,
            19.8809475
          ],
          [
            78.0876061,
            19.8820812
          ]
        ]
      ]
    },
    "bbox": [
      78.08708534255405,
      19.879158711549398,
      78.09133114181135,
      19.88209039592277
    ]
  },
  {
    "id": "P-008",
    "survey_number": "8",
    "ror_owner_name": "Balasaheb Dashrath Thorat",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 6.04,
    "current_area_ha": 6.16,
    "area_delta_pct": 1.99,
    "triage_state": "FLAGGED",
    "reason_codes": [
      "BOUNDARY_DISPLACEMENT_EXCEEDS_TOLERANCE"
    ],
    "match_type": "ONE_TO_ONE",
    "match_confidence": 0.74,
    "asbd_m": 2.65,
    "occlusion_fraction": 0.12,
    "support_ratio_pct": 62.0,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "479b00b8b2548b7121f9ffeb8d99fcef33de7fa57e066ddb1e409062a4734501",
    "parent_hash": "3f49e6000ebd84fc6185f4e711d85589abdf76a80a57c7b6c599462e224e5c93",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0880827,
            19.883162
          ],
          [
            78.0876091,
            19.8820909
          ],
          [
            78.0916554,
            19.8808505
          ],
          [
            78.0919436,
            19.8817248
          ],
          [
            78.0918407,
            19.8822385
          ],
          [
            78.0880827,
            19.883162
          ]
        ]
      ]
    },
    "bbox": [
      78.08758511711389,
      19.88083771080077,
      78.09197795763754,
      19.883169273483002
    ]
  },
  {
    "id": "P-009",
    "survey_number": "9",
    "ror_owner_name": "Kailas Manikrao Ingle",
    "source": "IMPORTED_BHUNAKSHA",
    "recorded_area_ha": 2.34,
    "current_area_ha": 2.38,
    "area_delta_pct": 1.71,
    "triage_state": "CLEARED",
    "reason_codes": [
      "CLEAR_BOUNDARY"
    ],
    "match_type": "ONE_TO_ONE",
    "match_confidence": 0.9,
    "asbd_m": 0.85,
    "occlusion_fraction": 0.04,
    "support_ratio_pct": 94.8,
    "verification_status": "UNVERIFIED",
    "version_number": 1,
    "current_hash": "4927d606bf7f27702a160ce8496dc66c27d340ab6ab8e5151c71fbf4e17d6b64",
    "parent_hash": "d4961ff9ade0377549696e1fc3e6ad69b622a062f8e670a70ab11990aeeb1652",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            78.0882604,
            19.8835349
          ],
          [
            78.0880816,
            19.8831641
          ],
          [
            78.0882157,
            19.8831033
          ],
          [
            78.0918366,
            19.8822431
          ],
          [
            78.0918634,
            19.8829544
          ],
          [
            78.0882604,
            19.8835349
          ]
        ]
      ]
    },
    "bbox": [
      78.08806966305154,
      19.88223909068392,
      78.09188423383787,
      19.883535908401345
    ]
  }
];

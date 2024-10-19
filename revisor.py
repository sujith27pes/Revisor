from flet import *
import math as m
import json
from random import randint as r
from random import choice as chooseOneFrom
import random
import asyncio

class HomePage(Column):
    def __init__(self, page: Page):
        super().__init__()
        self.expand = True
        self.testsTaken = page.client_storage.get("tests_taken", 0)
        self.history = page.client_storage.get("performance_history", [0])
        self.avgScore = (m.fsum(self.history)/(len(self.history)-1)) if len(self.history)>1 else 0
        
        self.mainRing = ProgressRing(
            width=256,
            height=256,
            stroke_width=50, 
            value=self.avgScore/100
        )
        
        self.quickInfo = Stack(
            controls=[
                Container(
                    content=Text(f"{self.avgScore:.1f}%", size=80, weight="bold"),
                    width=256,
                    height=256,
                    alignment=alignment.center
                ),
                self.mainRing,
            ],
            expand=1
        )

        self.overallinfo = Column(
            spacing=0,
            controls=[
                Text("Tests taken", size=32),
                Text(f"{self.testsTaken}", color="#66f9f9", size=64, weight="bold")
            ]
        )

        self.QuickInfoRow = Container(
            padding=Padding(top=100, bottom=0, left=0, right=0),
            content=Row(
                controls=[
                    Container(content=self.quickInfo, alignment=alignment.center),
                    self.overallinfo,
                ],
                alignment=MainAxisAlignment.CENTER,
                spacing=100
            )
        )

        data = [LineChartData(
            data_points=[LineChartDataPoint(i, self.history[i]) for i in range(len(self.history))],
            stroke_width=4,
            color=colors.with_opacity(0.5, "#66f9f9"),
            below_line_bgcolor=colors.with_opacity(0.2, "#66f9f9"),
            curved=True,
            stroke_cap_round=True
        )]

        self.progressChart = LineChart(
            horizontal_grid_lines=ChartGridLines(24),
            height=200,
            data_series=data,
            left_axis=ChartAxis(
                labels_interval=1,
                labels=[
                    ChartAxisLabel(value=0, label=Text("0%")),
                    ChartAxisLabel(value=25, label=Text("25%")),
                    ChartAxisLabel(value=50, label=Text("50%")),
                    ChartAxisLabel(value=75, label=Text("75%")),
                    ChartAxisLabel(value=100, label=Text("100%")),
                ],
                labels_size=40
            ),
            bottom_axis=ChartAxis(
                labels_interval=1,
                labels=[ChartAxisLabel(value=10*i, label=Text(str(10*i))) for i in range(1, (m.ceil(self.testsTaken/10))+1)],
                labels_size=32,
            ),
            min_y=0, min_x=0, max_y=100,
            animate=1000,
            expand=False
        )
        self.progressChart.data_series[0].point = False
        self.alignment = MainAxisAlignment.SPACE_BETWEEN
        self.controls = [
            self.QuickInfoRow,
            self.progressChart
        ]

class MaterialsPage(Column):
    def __init__(self, page: Page):
        super().__init__()
        self.visible = False
        self.page = page
        
        if page.client_storage.contains_key("stat.totalQs"):
            self.length = page.client_storage.get("stat.totalQs")
        else:
            page.client_storage.set('all_tags', [])
            page.client_storage.set("stat.totalQs", 0)
            page.client_storage.set('bank', [])
            self.length = 0
            
        self.uploadForm = Container(
            content=Row(
                controls=[
                    TextField(
                        label="Add MCQs (JSON)",
                        expand=1,
                        border_color="#FFFFFF",
                        multiline=True,
                    ),
                    FloatingActionButton(icon=icons.ADD, on_click=self.addMCQ)
                ],
                alignment=MainAxisAlignment.CENTER
            ),
            alignment=alignment.center
        )

        self.bankSize = Column(
            spacing=0,
            controls=[
                Container(
                    content=Text(f"{self.length}", color="#66f9f9", size=96, weight="bold"),
                    alignment=alignment.center
                ),
                Container(
                    content=Text("MCQs", size=16),
                    alignment=alignment.center
                ),
            ],
            alignment=MainAxisAlignment.CENTER
        )

        self.bankDisplay = Container(
            content=self.bankSize,
            alignment=alignment.center,
            expand=True
        )

        self.controls = [
            self.uploadForm,
            self.bankDisplay
        ]     
        self.expand = True

    def addMCQ(self, e):
        try:
            self.fullBank = self.page.client_storage.get("bank")
            self.all_tags = self.page.client_storage.get("all_tags")

            self.MCQ_objects = [json.loads(i) for i in self.uploadForm.content.controls[0].value.splitlines()]
            for mcq_obj in self.MCQ_objects:
                for tag in mcq_obj["t"]:
                    if tag not in self.all_tags:
                        self.all_tags.append(tag)
                self.fullBank.append(mcq_obj)
                
            self.page.client_storage.set("all_tags", self.all_tags)
            self.page.client_storage.set("bank", self.fullBank)
            self.uploadForm.content.controls[0].value = ''
            self.length += len(self.MCQ_objects)
            self.bankSize.controls[0].content.value = f'{self.length}'
            self.page.client_storage.set("stat.totalQs", self.length)
            self.page.update()
        except Exception as e:
            print(f"Error adding MCQs: {e}")

class Tags(Chip):
    def __init__(self, label):
        super().__init__(label=label)
        self.disabled_color = colors.TRANSPARENT
        self.bgcolor = colors.TRANSPARENT
        self.disabled = False
        self.on_select = self.toggle
        self.selected = False
        self.show_checkmark = False
    
    def toggle(self, e):
        pass

class MCQ(Container):
    def __init__(self, q, t, o, a):
        super().__init__()
        self.border_radius = 30
        self.padding = Padding(top=32, left=32, right=32, bottom=32)
        self.margin = Margin(left=24, top=24, right=24, bottom=24)
        self.bgcolor = colors.BLACK54
        self.Options = RadioGroup(
            content=Column([
                Radio(value=i, label=opt) for i, opt in enumerate(o)
            ])
        )
        self.content = Column(
            controls=[
                Text(value=q, size=32, color='#66f9f9'),
                self.Options
            ]
        )

class TestPage(Column):
    def __init__(self, page: Page):
        super().__init__()
        self.visible = False
        self.page = page
        self.all_tags = page.client_storage.get("all_tags", [])
        self.question_bank = page.client_storage.get("bank", [])
        self.selected_tags = []
        self.expand = True

        # Test configuration
        self.totalTestQs = 10
        self.test_duration = 15  # minutes
        self.test_mode = "q"  # q for quick, b for bundle
        self.difficulty = "e"  # e for easy, m for medium, h for hard
        self.TestMix = [7, 3, 0]  # default mix [easy, medium, hard]
        
        # Test state
        self.is_test_active = False
        self.test_score = 0
        self.time_remaining = 0
        self.student_answers = {}
        self.question_paper = []

        # Timer display
        self.timer_display = Text(f"{self.test_duration}:00", size=24, color="#66f9f9")
        
        # Score display
        self.score_display = Container(
            visible=False,
            content=Column([
                Text("Test Complete!", size=32, weight="bold"),
                Text("", size=48, color="#66f9f9", weight="bold"),  # Score percentage
            ], horizontal_alignment=CrossAxisAlignment.CENTER),
            alignment=alignment.center,
        )

        # Initialize chips for tags
        self.tagChips = [Tags(label=Text(i)) for i in self.all_tags]
        self.tagsSheet = BottomSheet(
            dismissible=True,
            content=Container(
                expand=True,
                content=Row(
                    tight=True,
                    controls=self.tagChips
                ),
            ),
            on_dismiss=self.tagsSet
        )

        # Test controls
        self.test_controls = Row(
            controls=[
                FilledButton(
                    text="Start Test",
                    visible=False,
                    on_click=self.start_test
                ),
                FilledButton(
                    text="Submit",
                    visible=False,
                    on_click=self.submit_test
                ),
                OutlinedButton(
                    text="End",
                    visible=False,
                    on_click=self.end_test
                )
            ],
            alignment=MainAxisAlignment.CENTER
        )

        # Initialize UI components
        self.init_test_options()
        
        self.testArea = Container(
            alignment=alignment.top_center,
            margin=Margin(0, 0, 0, 50),
            content=Column(
                controls=[],
                horizontal_alignment=CrossAxisAlignment.CENTER,
                scroll=ScrollMode.AUTO
            )
        )

        self.controls = [
            self.testModes,
            self.timer_display,
            self.testArea,
            self.test_controls,
            self.score_display
        ]

    def init_test_options(self):
        self.testModes = Container(
            alignment=alignment.center,
            content=Row(
                controls=[
                    SegmentedButton(
                        selected_icon=Icon(icons.RADIO_BUTTON_ON),
                        allow_multiple_selection=False,
                        selected={"q"},
                        segments=[
                            Segment(value="q", label=Text("Quick"), icon=Icon(icons.RADIO_BUTTON_OFF)),
                            Segment(value="b", label=Text("Bundle"), icon=Icon(icons.RADIO_BUTTON_OFF))
                        ],
                        on_change=self.select_testMode
                    ),
                    SegmentedButton(
                        selected_icon=Icon(icons.RADIO_BUTTON_ON),
                        allow_multiple_selection=False,
                        selected={"e"},
                        segments=[
                            Segment(value="e", label=Text("Easy"), icon=Icon(icons.RADIO_BUTTON_OFF)),
                            Segment(value="m", label=Text("Medium"), icon=Icon(icons.RADIO_BUTTON_OFF)),
                            Segment(value="h", label=Text("Hard"), icon=Icon(icons.RADIO_BUTTON_OFF))
                        ],
                        on_change=self.select_testDifficulty
                    ),
                    FilledButton(
                        text="Generate Test",
                        on_click=self.generateTest
                    ),
                    IconButton(icon=icons.SETTINGS, on_click=self.tagsSelection)
                ],
                alignment=MainAxisAlignment.CENTER
            )
        )

    def generateTest(self, e):
        if not self.selected_tags:
            return  # Show error message that tags must be selected
        
        self.question_paper = []
        questions_by_difficulty = {
            "easy": [],
            "medium": [],
            "hard": []
        }
        
        # Sort available questions by difficulty
        for q in self.question_bank:
            if any(tag in q["t"] for tag in self.selected_tags):
                if "easy" in q["t"]:
                    questions_by_difficulty["easy"].append(q)
                elif "medium" in q["t"]:
                    questions_by_difficulty["medium"].append(q)
                elif "hard" in q["t"]:
                    questions_by_difficulty["hard"].append(q)

        # Select questions according to TestMix
        for diff_idx, count in enumerate(self.TestMix):
            diff_type = ["easy", "medium", "hard"][diff_idx]
            available = questions_by_difficulty[diff_type]
            
            if len(available) < count:
                return  # Show error message about insufficient questions
                
            selected = random.sample(available, count)
            self.question_paper.extend(selected)
        
        random.shuffle(self.question_paper)
        
        # Create MCQ controls
        self.testArea.content.controls = [
            MCQ(q["q"], q["t"], q["o"], q["a"]) for q in self.question_paper
        ]
        
        # Show start button and hide generate button
        self.test_controls.controls[0].visible = True
        self.testModes.visible = False
        self.page.update()

    async def update_timer(self):
        while self.is_test_active and self.time_remaining > 0:
            minutes = self.time_remaining // 60
            seconds = self.time_remaining % 60
            self.timer_display.value = f"{minutes:02d}:{seconds:02d}"
            self.timer_display.update()
            await asyncio.sleep(1)
            self.time_remaining -= 1
            
        if self.time_remaining <= 0 and self.is_test_active:
            self.submit_test(None)

    def start_test(self, e):
        self.is_test_active = True
        self.time_remaining = self.test_duration * 60  # Convert to seconds
        self.test_controls.controls[0].visible = False  # Hide start button
        self.test_controls.controls[1].visible = True   # Show submit button
        self.test_controls.controls[2].visible = True   # Show end button
        
        asyncio.create_task(self.update_timer())
        self.page.update()

    def submit_test(self, e):
        if not self.is_test_active:
            return

        self.is_test_active = False
        correct_answers = 0
        
        # Collect answers from MCQ controls
        for i, mcq in enumerate(self.testArea.content.controls):
            if mcq.Options.value == self.question_paper[i]["a"]:
                correct_answers += 1
        
        score_percentage = (correct_answers / len(self.question_paper)) * 100
        
        # Update performance history
        history = self.page.client_storage.get("performance_history", [])
        history.append(score_percentage)
        self.page.client_storage.set("performance_history", history)
        
        tests_taken = self.page.client_storage.get("tests_taken",